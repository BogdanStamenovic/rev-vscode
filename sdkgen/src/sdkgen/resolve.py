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

        # 1. Nested types of the current class and its outers -- including
        #    types only *inherited* (via extends/implements) at each level.
        #    Java resolves an unqualified nested-type name through the
        #    superclass/superinterface chain before ever falling back to
        #    package or import lookup: `Direction` inside DcMotorImpl
        #    (`implements DcMotor`, which `extends DcMotorSimple`) means
        #    DcMotorSimple.Direction, declared nowhere near DcMotorImpl
        #    itself. Skipping this step (the pre-fix behavior) sent these
        #    names all the way to resolve_or_java_lang's `java.lang.<Name>`
        #    fallback -- a fabricated FQN that isn't in the registry at all.
        for outer_fqn in self.outer_chain():
            candidate = f"{outer_fqn}.{name}"
            if candidate in self.registry.by_fqn:
                return candidate
            for ancestor_fqn in _ancestor_fqns(outer_fqn, self.registry):
                candidate = f"{ancestor_fqn}.{name}"
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


def _resolve_supertype_name(name: str, class_fqn: str, registry: Registry,
                             type_param_names: set[str]) -> str | None:
    """Resolves the head name of one of `class_fqn`'s own extends/implements
    entries -- i.e. rules 1-4 of resolve_simple_name, minus the ancestor
    search that rule 1 now also does. Kept as a separate, deliberately
    non-recursive function (rather than reusing TypeContext.resolve_simple_name
    directly) so that computing a class's ancestors can never recurse back
    into the very ancestor-search it's computing for: a class header naming
    its own supertype is essentially always a plain nested/package/imported
    name, never itself something that needs inherited-nested-type lookup."""
    if name in type_param_names:
        return name
    entry = registry.by_fqn.get(class_fqn)
    cu = entry.cu if entry else None
    package = entry.package if entry else ""

    fqn: str | None = class_fqn
    while fqn is not None:
        candidate = f"{fqn}.{name}"
        if candidate in registry.by_fqn:
            return candidate
        fqn = registry.by_fqn[fqn].outer_fqn if fqn in registry.by_fqn else None

    if package:
        candidate = f"{package}.{name}"
        if candidate in registry.by_fqn:
            return candidate
    elif name in registry.by_fqn:
        return name

    if cu is not None:
        for imp in cu.imports:
            if imp.wildcard or imp.static:
                continue
            if imp.path.rsplit(".", 1)[-1] == name:
                return imp.path
        for imp in cu.imports:
            if imp.wildcard and not imp.static:
                candidate = f"{imp.path}.{name}"
                if candidate in registry.by_fqn:
                    return candidate
    return None


def _direct_supertype_fqns(fqn: str, registry: Registry) -> list[str]:
    """The FQNs of `fqn`'s own `extends`/`implements` clauses (one level,
    not transitive)."""
    entry = registry.by_fqn.get(fqn)
    if entry is None:
        return []
    node = entry.node
    type_param_names = _collect_type_params(getattr(node, "type_parameters", None))

    raw_nodes = []
    ext = getattr(node, "extends", None)
    if ext:
        raw_nodes.extend(ext if isinstance(ext, list) else [ext])
    impl = getattr(node, "implements", None)
    if impl:
        raw_nodes.extend(impl)

    out = []
    for t in raw_nodes:
        names, _ = _chain_names_and_args(t)
        if not names:
            continue
        resolved = _resolve_supertype_name(names[0], fqn, registry, type_param_names)
        if resolved is None:
            continue
        candidate = ".".join([resolved] + names[1:])
        if candidate in registry.by_fqn:
            out.append(candidate)
    return out


def _ancestor_fqns(fqn: str, registry: Registry) -> list[str]:
    """Transitive extends/implements closure of `fqn`, direct bases first,
    memoized on the registry for the life of one generator run (the
    registry is rebuilt fresh per invocation, so this can't leak across
    unrelated runs within one process, e.g. under pytest)."""
    cache = registry.ancestor_cache
    if fqn in cache:
        return cache[fqn]
    cache[fqn] = []  # cycle guard -- Java itself disallows real inheritance cycles
    result: list[str] = []
    seen = {fqn}
    for direct in _direct_supertype_fqns(fqn, registry):
        if direct not in seen:
            seen.add(direct)
            result.append(direct)
        for ancestor in _ancestor_fqns(direct, registry):
            if ancestor not in seen:
                seen.add(ancestor)
                result.append(ancestor)
    cache[fqn] = result
    return result


def resolve_qualified_chain(base_fqn: str, remaining: list[str], registry: Registry) -> str:
    """Walks a dotted qualifier chain (e.g. `DcMotor.Direction`) one segment
    at a time, checking each segment against the current FQN's own nested
    types first and its ancestor chain second -- mirroring Java's rule that
    `Outer.Nested` is legal even when `Nested` is only inherited by `Outer`,
    not declared there. `DcMotor.Direction` is exactly this: DcMotor extends
    DcMotorSimple, and Direction is nested in DcMotorSimple, not DcMotor.
    The pre-fix caller here blindly concatenated `base_fqn + "." + name`
    with no existence check at all, so it baked a *guaranteed-wrong* FQN
    (`...DcMotor.Direction`, absent from the registry) straight into the
    type database -- not a fallback, actual corruption. A segment that
    still can't be found anywhere (own nested types or ancestors) falls
    back to the same blind concatenation, so callers keep getting a
    deterministic string rather than an exception; extract.py's own
    `unresolvable` bookkeeping is what surfaces that case downstream."""
    current = base_fqn
    for name in remaining:
        candidate = f"{current}.{name}"
        if candidate in registry.by_fqn:
            current = candidate
            continue
        found = None
        for ancestor_fqn in _ancestor_fqns(current, registry):
            ancestor_candidate = f"{ancestor_fqn}.{name}"
            if ancestor_candidate in registry.by_fqn:
                found = ancestor_candidate
                break
        current = found if found is not None else candidate
    return current


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
                base = resolve_qualified_chain(first_resolved, names[1:], ctx.registry)
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
