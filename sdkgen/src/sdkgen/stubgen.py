"""Emits python/ftc/*.py (Contract 2) from the Contract-1 `classes` dict.

One file per module (opmode/hardware/telemetry/navigation/util/vision).
Cross-module base classes are real top-level imports (there are no import
cycles between our module set -- verified empirically: hardware and vision
depend on opmode/util, nothing depends back). Cross-module types used only
in parameter/return/field position are imported under `TYPE_CHECKING`,
which is always safe (with `from __future__ import annotations`, those
annotations are never evaluated at runtime) and keeps the generator robust
if a future SDK version *does* introduce a cycle.
"""
from __future__ import annotations

import keyword
import re
import sys
from pathlib import Path

import javalang.tree as jt

from .pytypes import RenderContext
from .registry import Registry
from .resolve import TypeContext, type_node_to_string, _collect_type_params

MODULES = ["ftc.opmode", "ftc.hardware", "ftc.telemetry", "ftc.navigation", "ftc.util", "ftc.vision",
           "ftc.internal"]

# ftc.internal has no Contract-2 package mapping of its own (see
# sdkgen/src/sdkgen/dbwrite.py FALLBACK_MODULE): it's the catch-all for a
# class that closure pulled in only because a stubbed signature mentions it.
MODULE_DOCSTRINGS = {
    "ftc.internal": (
        "Types pulled in only so a stubbed signature elsewhere (e.g. "
        "DcMotor.getMotorType() -> MotorConfigurationType) resolves to a "
        "real class instead of Any. None of these have a Contract-2 package "
        "mapping of their own; users don't normally import from here directly."
    ),
}

JAVA_EXCEPTION_BASES = {
    "java.lang.RuntimeException": "Exception",
    "java.lang.Exception": "Exception",
    "java.lang.Error": "Exception",
    "java.lang.Throwable": "BaseException",
    "java.lang.IllegalArgumentException": "ValueError",
    "java.lang.IllegalStateException": "RuntimeError",
    "java.lang.InterruptedException": "InterruptedError",
}


def sanitize_ident(name: str) -> str:
    name = name.replace("$", "_")
    if keyword.iskeyword(name) or name in ("self", "cls"):
        return name + "_"
    return name


_FQN_TOKEN_RE = re.compile(r"[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*")


def collect_referenced_fqns(type_str: str, classes: dict) -> set[str]:
    found = set()
    for token in _FQN_TOKEN_RE.findall(type_str):
        parts = token.split(".")
        for i in range(len(parts), 0, -1):
            candidate = ".".join(parts[:i])
            if candidate in classes:
                found.add(candidate)
    return found


def _pure_filtered_bases(fqn: str, classes: dict) -> list[str]:
    """Same redundant-ancestor pruning as ModuleWriter._dedupe_redundant_bases,
    but as a free function over the whole `classes` graph (module-agnostic),
    for use while precomputing global MRO -- a diamond is a structural
    property of the Java type graph, independent of which module ends up
    stubbing which class."""
    raw = _dedupe_preserve_order(_strip_generics_arrays(e) for e in classes.get(fqn, {}).get("extends", []))
    raw = [b for b in raw if b in classes]
    cache: dict = {}

    def ancestors(f: str) -> set[str]:
        if f in cache:
            return cache[f]
        cache[f] = set()
        result = set()
        for b in _dedupe_preserve_order(_strip_generics_arrays(e) for e in classes.get(f, {}).get("extends", [])):
            if b in classes:
                result.add(b)
                result |= ancestors(b)
        cache[f] = result
        return result

    return [b for b in raw if not any(b in ancestors(o) for o in raw if o != b)]


def _c3_merge(sequences: list[list[str]]) -> list[str] | None:
    seqs = [list(s) for s in sequences if s]
    result: list[str] = []
    while True:
        seqs = [s for s in seqs if s]
        if not seqs:
            return result
        head = None
        for s in seqs:
            candidate = s[0]
            if not any(candidate in other[1:] for other in seqs):
                head = candidate
                break
        if head is None:
            return None
        result.append(head)
        for s in seqs:
            if s and s[0] == head:
                s.pop(0)


def compute_global_mro_cache(classes: dict) -> dict[str, list[str]]:
    """Precomputes each class's Python-style C3 MRO over the structural
    (redundancy-pruned) Java extends graph, memoized once for the whole run."""
    cache: dict[str, list[str]] = {}
    computing: set[str] = set()

    def compute(fqn: str) -> list[str]:
        if fqn in cache:
            return cache[fqn]
        if fqn in computing:
            return [fqn]  # cyclic (shouldn't happen); break defensively
        computing.add(fqn)
        bases = _pure_filtered_bases(fqn, classes)
        if not bases:
            result = [fqn]
        else:
            parent_mros = [compute(b) for b in bases]
            merged = _c3_merge(parent_mros + [list(bases)])
            if merged is None:
                # The bases themselves are already pairwise non-redundant,
                # so a conflict here is a genuine diamond with incompatible
                # internal orderings. Best-effort: dedupe-concatenate.
                merged = _dedupe_preserve_order([f for m in parent_mros for f in m] + bases)
            result = [fqn] + merged
        computing.discard(fqn)
        cache[fqn] = result
        return result

    for fqn in classes:
        compute(fqn)
    return cache


def _dedupe_preserve_order(items) -> list[str]:
    seen: set[str] = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _strip_generics_arrays(type_str: str) -> str:
    return type_str.split("<", 1)[0].rstrip("[]")


def _format_docstring(text: str, indent: str) -> list[str]:
    if not text:
        return []
    # Escape backslashes and quotes so embedded `"` (common in javadoc,
    # e.g. quoted string examples) can never collide with the """ delimiter.
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    return [f'{indent}"""{text}"""']


def _children_map(classes: dict) -> dict[str, list[str]]:
    m: dict[str, list[str]] = {}
    for f, c in classes.items():
        if c["outer"]:
            m.setdefault(c["outer"], []).append(f)
    return m


def _topo_sort(fqns: list[str], classes: dict, module: str) -> list[str]:
    """Orders `fqns` (either all top-level classes of a module, or the
    direct nested children of one class) so a same-module base class is
    always emitted before its subclass. Dependencies are computed through
    the full nested closure of each entry, because a nested class's base
    (e.g. `LynxController.PretendLynxModule extends LynxModuleIntf`) can
    reference a sibling *top-level* class that ordinary top-level-only
    dependency analysis would miss."""
    fqn_set = set(fqns)
    children = _children_map(classes)
    order: list[str] = []
    state: dict[str, int] = {}  # 0=unvisited,1=visiting,2=done

    def closure(fqn: str) -> list[str]:
        stack, out = [fqn], []
        while stack:
            cur = stack.pop()
            out.append(cur)
            stack.extend(children.get(cur, []))
        return out

    def top_ancestor(fqn: str) -> str:
        while classes[fqn]["outer"]:
            fqn = classes[fqn]["outer"]
        return fqn

    def deps(fqn: str) -> list[str]:
        out = set()
        for member in closure(fqn):
            for ext in classes[member]["extends"]:
                base = _strip_generics_arrays(ext)
                if base not in classes:
                    continue
                if base in fqn_set:
                    out.add(base)
                else:
                    base_top = top_ancestor(base)
                    if base_top in fqn_set:
                        out.add(base_top)
        out.discard(fqn)
        return out

    def visit(fqn: str) -> None:
        s = state.get(fqn, 0)
        if s == 2:
            return
        if s == 1:
            print(f"sdkgen: inheritance cycle involving {fqn} in {module}, breaking arbitrarily",
                  file=sys.stderr)
            return
        state[fqn] = 1
        for d in deps(fqn):
            visit(d)
        state[fqn] = 2
        order.append(fqn)

    for fqn in fqns:
        visit(fqn)
    return order


def _default_expr(node) -> str | None:
    if node is None:
        return None
    if isinstance(node, jt.Literal):
        v = node.value
        if v is None:
            return None
        if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
            return repr(v[1:-1].encode().decode("unicode_escape"))
        if v in ("true", "false"):
            return "True" if v == "true" else "False"
        numeric = v.rstrip("dDfFlL")
        return numeric or "0"
    return None


class ModuleWriter:
    def __init__(self, module: str, classes: dict, registry: Registry, mro_cache: dict[str, list[str]]):
        self.module = module
        self.classes = classes
        self.registry = registry
        self.mro_cache = mro_cache
        self.ctx = RenderContext(classes=classes, module_of={}, current_module=module)
        self.emitted: set[str] = set()
        self.body_lines: list[str] = []
        self.needs_enum = False

    def _resolve_consistent_bases(self, fqn: str, base_fqns: list[str]) -> list[str]:
        """Verifies the candidate base list actually linearizes under
        Python's C3 rule (a diamond can be structurally pruned per-base via
        _dedupe_redundant_bases and still conflict, if two *unrelated*
        bases each pulled in a shared ancestor through a different internal
        order). Drops bases from the end -- least likely to be the
        "primary" type -- until consistent."""
        candidates = list(base_fqns)
        while candidates:
            parent_mros = [self.mro_cache.get(b, [b]) for b in candidates]
            if _c3_merge(parent_mros + [list(candidates)]) is not None:
                return candidates
            dropped = candidates.pop()
            print(f"sdkgen: dropping base {dropped} of {fqn} to resolve an MRO conflict "
                  f"among its bases (Java interfaces don't have Python's C3 constraint)",
                  file=sys.stderr)
        return candidates

    # -- class-name path helpers -------------------------------------------------
    def _nested_path(self, fqn: str) -> list[str]:
        c = self.classes[fqn]
        path = [c["simpleName"]]
        cur = c["outer"]
        while cur:
            cc = self.classes[cur]
            path.append(cc["simpleName"])
            cur = cc["outer"]
        path.reverse()
        return path

    def _transitive_java_ancestors(self, fqn: str, cache: dict) -> set[str]:
        if fqn in cache:
            return cache[fqn]
        cache[fqn] = set()  # break cycles defensively
        result: set[str] = set()
        for ext in self.classes.get(fqn, {}).get("extends", []):
            base = _strip_generics_arrays(ext)
            if base in self.classes:
                result.add(base)
                result |= self._transitive_java_ancestors(base, cache)
        cache[fqn] = result
        return result

    def _dedupe_redundant_bases(self, fqn: str, base_fqns: list[str]) -> list[str]:
        """Java interfaces freely form diamonds (`implements A, B` where B
        already extends A); Python's C3 linearization rejects listing an
        ancestor both directly and via another base. Drop a base if it's
        already implied (transitively) by another base in the same list --
        its members are still inherited, just through the more-derived base."""
        cache: dict = {}
        ancestors_of = {b: self._transitive_java_ancestors(b, cache) for b in base_fqns}
        keep = []
        for b in base_fqns:
            implied_elsewhere = any(b in ancestors_of[other] for other in base_fqns if other != b)
            if implied_elsewhere:
                print(f"sdkgen: dropping redundant base {b} of {fqn} (already implied by "
                      f"another listed base -- Java diamond, avoids an MRO conflict)",
                      file=sys.stderr)
                continue
            keep.append(b)
        return keep

    # -- bases --------------------------------------------------------------
    def _render_bases(self, fqn: str, type_param_names: list[str]) -> list[str]:
        c = self.classes[fqn]
        bases: list[str] = []
        extends_fqns = _dedupe_preserve_order(_strip_generics_arrays(e) for e in c["extends"])
        extends_fqns = self._dedupe_redundant_bases(fqn, extends_fqns)
        extends_fqns = self._resolve_consistent_bases(fqn, extends_fqns)
        ext_by_fqn = {_strip_generics_arrays(e): e for e in c["extends"]}
        for base_fqn in extends_fqns:
            ext = ext_by_fqn[base_fqn]
            if base_fqn in JAVA_EXCEPTION_BASES:
                bases.append(JAVA_EXCEPTION_BASES[base_fqn])
                continue
            if base_fqn not in self.classes:
                continue  # JDK/unmodeled type -- can't be a Python base, dropped
            resolved = self.ctx.top_level_path(base_fqn)
            if resolved is None:
                continue  # base lives outside our stubbed modules
            owning_module, path = resolved
            if owning_module == self.module:
                if base_fqn not in self.emitted:
                    print(f"sdkgen: dropping forward-referenced base {base_fqn} of {fqn} "
                          f"(same-module ordering limitation)", file=sys.stderr)
                    continue
                # Python class bodies don't nest lexical scope the way
                # functions do: a class statement can only see names bound
                # earlier in its own *immediate* enclosing body (or the
                # module scope). A dotted reference like `Outer.Sibling` is
                # only valid once `Outer` itself has finished executing (is
                # bound at module scope) -- which it hasn't, if we're still
                # inside Outer's own body. So a nested class referencing an
                # already-emitted *sibling* (direct or indirect, under the
                # same still-open outer) must use a name relative to that
                # shared open body, not the full dotted path from the top.
                outer_fqn = c["outer"]
                scope_path = self._nested_path(outer_fqn) if outer_fqn else []
                if scope_path and path[: len(scope_path)] == scope_path:
                    rel = path[len(scope_path):]
                    if not rel:
                        print(f"sdkgen: dropping base {base_fqn} of {fqn} (a nested class "
                              f"extending its own still-open outer class has no valid Python "
                              f"spelling)", file=sys.stderr)
                        continue
                    path = rel
            else:
                self.ctx._record_import(owning_module, path[0], runtime=True)
            expr = ".".join(path)
            base_c = self.classes.get(base_fqn)
            arg_node_strs = self._extract_generic_args(ext)
            if arg_node_strs and base_c and base_c.get("typeParams"):
                # A generic argument to a base class is also eagerly
                # evaluated. Java allows a class to parameterize one of its
                # own bases with itself or one of its own (still-open)
                # nested types (e.g. `... extends Foo<Foo.Parameters>`);
                # Python can't express that at class-definition time, so if
                # any referenced type isn't fully emitted yet, drop the
                # subscript and keep the bare (non-generic) base instead.
                referenced = set()
                for a in arg_node_strs:
                    referenced |= collect_referenced_fqns(a, self.classes)
                if referenced <= self.emitted:
                    rendered_args = [self.ctx.render(a, runtime=True) for a in arg_node_strs]
                    expr += f"[{', '.join(rendered_args)}]"
                else:
                    unemitted = referenced - self.emitted
                    print(f"sdkgen: dropping generic args of base {base_fqn} on {fqn} "
                          f"(self-referential: {sorted(unemitted)})", file=sys.stderr)
            bases.append(expr)
        if type_param_names:
            # Generic[...] goes *after* real bases, not before: it has to
            # for the same MRO-ordering reason as enum.Enum below -- listing
            # it first was fine while every generic stubbed class had zero
            # or one same-kind base, but closure pulled in
            # Continuation.Dispatcher(Generic[S], MemberwiseCloneable),
            # where Generic-first is an unresolvable MRO for CPython.
            bases.append(f"Generic[{', '.join(type_param_names)}]")
        if c["kind"] == "enum":
            self.needs_enum = True
            # enum.Enum must come *last*: mixing it with another base (a
            # Java enum implementing an interface) only works in Python if
            # the plain classes come first and Enum-derived closes the MRO
            # (see enum.EnumMeta._get_mixins_) -- putting it first, as a
            # single unconditional `bases.append("enum.Enum")` up front used
            # to do, raises "new enumerations should be created as
            # EnumName([mixin_type, ...] [data_type,] enum_type)" the first
            # time closure pulls in an enum that implements something.
            bases.append("enum.Enum")
        return bases

    @staticmethod
    def _extract_generic_args(type_str: str) -> list[str]:
        from .pytypes import parse_type_str
        node = parse_type_str(type_str)
        return [_reconstruct(a) for a in node.args]

    # -- members --------------------------------------------------------------
    def _render_method_group(self, name: str, methods: list[dict], indent: str,
                              is_ctor: bool = False) -> list[str]:
        name = "__init__" if is_ctor else sanitize_ident(name)
        lines = []
        overload = len(methods) > 1
        any_static = any(m.get("static") for m in methods)
        all_static = all(m.get("static") for m in methods)
        for m in methods:
            is_static = bool(m.get("static")) if not is_ctor else False
            if overload:
                lines.append(f"{indent}@overload")
            if is_static:
                lines.append(f"{indent}@staticmethod")
            params = [] if is_static else ["self"]
            for i, p in enumerate(m["params"]):
                pname = sanitize_ident(p["name"])
                t = self.ctx.render(p["type"])
                if p["varargs"] and i == len(m["params"]) - 1:
                    params.append(f"*{pname}: {t}")
                else:
                    params.append(f"{pname}: {t}")
            ret = "None" if is_ctor else self.ctx.render(m["returns"])
            sig_name = "__init__" if is_ctor else name
            lines.append(f"{indent}def {sig_name}({', '.join(params)}) -> {ret}:")
            doc = _format_docstring(m.get("doc", ""), indent + "    ")
            lines.extend(doc)
            lines.append(f"{indent}    ...")
        if overload:
            sig_name = "__init__" if is_ctor else name
            head = "self, *args: Any, **kwargs: Any" if not all_static else "*args: Any, **kwargs: Any"
            if all_static:
                lines.append(f"{indent}@staticmethod")
            ret = "None" if is_ctor else "Any"
            lines.append(f"{indent}def {sig_name}({head}) -> {ret}:")
            lines.append(f"{indent}    ...")
        return lines

    def _render_fields(self, fields: list[dict], indent: str, taken_names: set[str]) -> list[str]:
        lines = []
        for f in fields:
            name = sanitize_ident(f["name"])
            if name in taken_names:
                # Java allows a field and a method of the same name (call
                # syntax disambiguates); Python's class namespace can't
                # hold both under one name, so the field loses the name
                # and gets a trailing underscore instead of silently
                # obscuring the method (which is almost always the more
                # useful member to keep reachable under its plain name).
                name = name + "_"
            t = self.ctx.render(f["type"])
            doc = f.get("doc", "")
            lines.append(f"{indent}{name}: {t}")
            if doc:
                lines.extend(_format_docstring(doc, indent))
        return lines

    def _render_class(self, fqn: str, indent: str) -> list[str]:
        c = self.classes[fqn]
        kind = c["kind"]
        simple = c["simpleName"]

        if kind == "annotation":
            return self._render_annotation_decorator(fqn, indent)

        type_params = c.get("typeParams") or []
        tv_names = []
        for tp in type_params:
            if " extends " in tp:
                tvname, bound = tp.split(" extends ", 1)
                tvname = tvname.strip()
                # A forward-reference *string* bound (not an eagerly evaluated
                # expression): the bound class may be defined later in this
                # same file (TypeVar declarations are emitted once, up top),
                # or even not meant to be imported at runtime at all. Python's
                # typing module explicitly supports this form.
                self.ctx.typevars_seen[tvname] = self.ctx.render(bound.strip(), runtime=False)
            else:
                tvname = tp.strip()
                self.ctx.typevars_seen.setdefault(tvname, None)
            tv_names.append(tvname)

        bases = self._render_bases(fqn, tv_names)
        base_str = f"({', '.join(bases)})" if bases else ""
        lines = [f"{indent}class {simple}{base_str}:"]
        body: list[str] = []
        body.extend(_format_docstring(c.get("doc", ""), indent + "    "))
        body.append(f'{indent}    __java__ = "{fqn}"')

        if kind == "enum":
            for const in c["enumConstants"]:
                # A Java enum constant can legally be spelled `None`, `True`,
                # etc. (they're ordinary identifiers in Java, not reserved) --
                # e.g. org.firstinspires...Camera.Error.None. sanitize_ident
                # is what keeps that from being a Python SyntaxError.
                body.append(f"{indent}    {sanitize_ident(const)} = enum.auto()")

        # Nested classes first (so later members that reference them as types
        # within the same class don't matter -- Python doesn't need forward
        # nested-class ordering the way base classes do).
        nested_fqns = [f for f, cc in self.classes.items() if cc["outer"] == fqn]
        nested_fqns = _topo_sort(nested_fqns, self.classes, self.module) if nested_fqns else []
        for nfqn in nested_fqns:
            self.emitted.add(nfqn)
            body.extend(self._render_class(nfqn, indent + "    "))
            body.append("")

        ctors = c.get("constructors") or []
        if ctors:
            body.extend(self._render_method_group("__init__", ctors, indent + "    ", is_ctor=True))
            body.append("")

        by_name: dict[str, list[dict]] = {}
        for m in c.get("methods") or []:
            by_name.setdefault(m["name"], []).append(m)
        for mname, group in by_name.items():
            body.extend(self._render_method_group(mname, group, indent + "    "))
            body.append("")

        method_names = {sanitize_ident(m["name"]) for m in c.get("methods") or []}
        body.extend(self._render_fields(c.get("fields") or [], indent + "    ", method_names))

        if len(body) == 2 and not ctors and not by_name and not (c.get("fields")):
            # Only docstring + __java__ -- fine, still valid non-empty body.
            pass
        # Trim a single trailing blank line for tidiness.
        while body and body[-1] == "":
            body.pop()
        lines.extend(body)
        return lines

    def _render_annotation_decorator(self, fqn: str, indent: str) -> list[str]:
        entry = self.registry.by_fqn[fqn]
        node = entry.node
        simple = node.name
        elements = list(node.body)
        c = self.classes[fqn]
        first_doc = c.get("doc", "")

        if not elements:
            lines = [f"{indent}def {simple}(cls: type) -> type:"]
            lines.extend(_format_docstring(first_doc, indent + "    ") or [f'{indent}    """{simple} marker annotation."""'])
            lines.append(f"{indent}    return cls")
            return lines

        ctx_local = TypeContext(registry=self.registry, class_fqn=fqn,
                                 type_param_names=set())
        params = []
        for elem in elements:
            pname = sanitize_ident(elem.name)
            ptype_str = type_node_to_string(elem.return_type, ctx_local)
            ptype = self.ctx.render(ptype_str)
            default = _default_expr(elem.default)
            if default is not None:
                params.append(f"{pname}: {ptype} = {default}")
            else:
                params.append(f"{pname}: {ptype}")

        lines = [f"{indent}def {simple}(*, {', '.join(params)}) -> Callable[[type], type]:"]
        lines.extend(_format_docstring(first_doc, indent + "    "))
        lines.append(f"{indent}    def _decorator(cls: type) -> type:")
        lines.append(f"{indent}        return cls")
        lines.append(f"{indent}    return _decorator")
        return lines

    # -- top level --------------------------------------------------------------
    def render(self, top_fqns: list[str]) -> str:
        ordered = _topo_sort(top_fqns, self.classes, self.module)
        for fqn in ordered:
            self.body_lines.extend(self._render_class(fqn, ""))
            self.emitted.add(fqn)
            self.body_lines.append("")
            self.body_lines.append("")

        header = self._build_header()
        return header + "\n" + "\n".join(self.body_lines).rstrip() + "\n"

    def _build_header(self) -> str:
        lines = []
        module_doc = MODULE_DOCSTRINGS.get(self.module)
        if module_doc:
            # A module docstring is allowed before `from __future__ import
            # annotations` (the one exception to "future imports must be the
            # first statement"), so this doesn't disturb the future import.
            lines.append(f'"""{module_doc}"""')
            lines.append("")
        lines.append("from __future__ import annotations")
        lines.append("")
        lines.append("from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload")
        if self.needs_enum:
            lines.append("import enum")
        lines.append("")

        for module in sorted(self.ctx.runtime_imports):
            names = ", ".join(sorted(self.ctx.runtime_imports[module]))
            lines.append(f"from {module} import {names}")

        tc_imports = {m: names - self.ctx.runtime_imports.get(m, set())
                      for m, names in self.ctx.type_checking_imports.items()}
        tc_imports = {m: n for m, n in tc_imports.items() if n}
        if tc_imports:
            lines.append("if TYPE_CHECKING:")
            for module in sorted(tc_imports):
                names = ", ".join(sorted(tc_imports[module]))
                lines.append(f"    from {module} import {names}")

        lines.append("")
        for name in sorted(self.ctx.typevars_seen):
            bound = self.ctx.typevars_seen[name]
            if bound:
                bound_literal = bound.replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'{name} = TypeVar("{name}", bound="{bound_literal}")')
            else:
                lines.append(f'{name} = TypeVar("{name}")')
        return "\n".join(lines)


def _reconstruct(node) -> str:
    """Turns a pytypes.TypeNode back into a type string (used for base-class
    generic arguments, which arrive pre-parsed from _extract_generic_args)."""
    s = node.base
    if node.args:
        s += "<" + ", ".join(_reconstruct(a) for a in node.args) + ">"
    s += "[]" * node.array_dims
    return s


def module_top_level_fqns(classes: dict, module: str) -> list[str]:
    return [fqn for fqn, c in classes.items() if c["outer"] is None and c["module"] == module]


def generate_module_files(classes: dict, registry: Registry, out_dir: Path) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    mro_cache = compute_global_mro_cache(classes)
    counts = {}
    for module in MODULES:
        top_fqns = module_top_level_fqns(classes, module)
        writer = ModuleWriter(module, classes, registry, mro_cache)
        text = writer.render(top_fqns)
        filename = module.split(".", 1)[1] + ".py"
        (out_dir / filename).write_text(text, encoding="utf-8")
        counts[module] = len(top_fqns)
    return counts
