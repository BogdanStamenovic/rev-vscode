"""Simple-name -> FQN resolution and javalang type-node -> Contract-1 type
string rendering.

Resolution order (per ARCHITECTURE.md Contract 1): nested types of the
current class and its outers, same package, single-type imports, on-demand
imports (resolved against known classes), then java.lang.<name>.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import javalang.tree as jt

from .registry import Registry

PRIMITIVES = {"int", "double", "boolean", "void", "long", "short", "byte", "char", "float"}


@dataclass
class TypeContext:
    """Everything needed to resolve simple names seen while looking at one
    class's members (or the class's own header, e.g. `extends`)."""

    registry: Registry
    class_fqn: str  # the class this member is declared in (innermost)
    type_param_names: set[str] = field(default_factory=set)  # in scope: class + method type params

    def outer_chain(self) -> list[str]:
        chain = []
        fqn: str | None = self.class_fqn
        while fqn is not None:
            chain.append(fqn)
            fqn = self.registry.by_fqn[fqn].outer_fqn if fqn in self.registry.by_fqn else None
        return chain

    def resolve_simple_name(self, name: str) -> str | None:
        """Returns an FQN if `name` resolves via a known rule, else None."""
        if name in self.type_param_names:
            return name  # caller checks type params separately; kept for safety
        entry = self.registry.by_fqn.get(self.class_fqn)
        cu = entry.cu if entry else None
        package = entry.package if entry else ""

        # 1. Nested types of the current class and its outers.
        for outer_fqn in self.outer_chain():
            candidate = f"{outer_fqn}.{name}"
            if candidate in self.registry.by_fqn:
                return candidate

        # 2. Same package.
        if package:
            candidate = f"{package}.{name}"
            if candidate in self.registry.by_fqn:
                return candidate
        else:
            if name in self.registry.by_fqn:
                return name

        # 3. Single-type imports.
        if cu is not None:
            for imp in cu.imports:
                if imp.wildcard or imp.static:
                    continue
                if imp.path.rsplit(".", 1)[-1] == name:
                    return imp.path

        # 4. On-demand imports (import x.y.*;), resolved against known classes.
        if cu is not None:
            for imp in cu.imports:
                if imp.wildcard and not imp.static:
                    candidate = f"{imp.path}.{name}"
                    if candidate in self.registry.by_fqn:
                        return candidate

        return None

    def resolve_or_java_lang(self, name: str) -> str:
        resolved = self.resolve_simple_name(name)
        if resolved is not None:
            return resolved
        return f"java.lang.{name}"


def _collect_type_params(type_params) -> set[str]:
    if not type_params:
        return set()
    return {tp.name for tp in type_params}


def type_params_to_strings(type_params, ctx: TypeContext) -> list[str]:
    """Renders e.g. ["T extends com.qualcomm...HardwareDevice"]."""
    if not type_params:
        return []
    out = []
    for tp in type_params:
        if tp.extends:
            bounds = " & ".join(type_node_to_string(b, ctx) for b in tp.extends)
            out.append(f"{tp.name} extends {bounds}")
        else:
            out.append(tp.name)
    return out


def _chain_names_and_args(node):
    """Walks a possibly-qualified ReferenceType (a.b.C<T>) and returns
    (list_of_segment_names, generic_arguments_of_last_segment_with_args)."""
    names = []
    args = None
    cur = node
    while cur is not None:
        names.append(cur.name)
        if getattr(cur, "arguments", None):
            args = cur.arguments
        cur = getattr(cur, "sub_type", None)
    return names, args


def type_node_to_string(node, ctx: TypeContext) -> str:
    if node is None:
        return "void"

    if isinstance(node, jt.BasicType):
        base = node.name
        dims = len(node.dimensions or [])
        return _wrap_array(base, dims)

    if isinstance(node, jt.ReferenceType):
        names, args = _chain_names_and_args(node)
        dims = len(node.dimensions or [])

        if len(names) == 1:
            name = names[0]
            if name in ctx.type_param_names:
                base = name  # bare type variable
            else:
                base = ctx.resolve_or_java_lang(name)
        else:
            first_resolved = ctx.resolve_simple_name(names[0]) if names[0] not in ctx.type_param_names else names[0]
            if first_resolved is not None:
                base = ".".join([first_resolved] + names[1:])
            else:
                base = ".".join(names)

        if args:
            arg_strs = [_type_argument_to_string(a, ctx) for a in args]
            base = f"{base}<{', '.join(arg_strs)}>"

        return _wrap_array(base, dims)

    # Fallback for unexpected node kinds.
    return "java.lang.Object"


def _type_argument_to_string(arg: jt.TypeArgument, ctx: TypeContext) -> str:
    if arg.type is None:
        return "java.lang.Object"  # bare `?`
    rendered = type_node_to_string(arg.type, ctx)
    # Wildcards (`? extends X` / `? super X`) have no Java-type-string
    # equivalent in our schema; we approximate by using the bound directly.
    # This is a documented deviation (see final report).
    return rendered


def _wrap_array(base: str, dims: int) -> str:
    return base + ("[]" * dims)
