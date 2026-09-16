"""Parses Contract-1 type strings (e.g. "java.util.List<com.qualcomm...Foo>",
"int[]", "T") and renders them as Python type-hint text for the stub
generator, tracking which cross-module imports each render needed.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TypeNode:
    base: str
    args: list["TypeNode"]
    array_dims: int


def _split_top_level_commas(s: str) -> list[str]:
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(s):
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(s[start:i])
            start = i + 1
    parts.append(s[start:])
    return [p.strip() for p in parts if p.strip()]


def parse_type_str(s: str) -> TypeNode:
    s = s.strip()
    array_dims = 0
    while s.endswith("[]"):
        array_dims += 1
        s = s[:-2].strip()
    if s.endswith(">") and "<" in s:
        idx = s.index("<")
        base = s[:idx]
        inner = s[idx + 1: -1]
        args = [parse_type_str(a) for a in _split_top_level_commas(inner)]
    else:
        base, args = s, []
    return TypeNode(base=base, args=args, array_dims=array_dims)


PRIMITIVE_MAP = {
    "int": "int", "double": "float", "float": "float", "boolean": "bool",
    "byte": "int", "short": "int", "long": "int", "char": "str", "void": "None",
}

JAVA_LANG_MAP = {
    "java.lang.String": "str", "java.lang.CharSequence": "str",
    "java.lang.Integer": "int", "java.lang.Short": "int", "java.lang.Byte": "int",
    "java.lang.Long": "int", "java.lang.Double": "float", "java.lang.Float": "float",
    "java.lang.Boolean": "bool", "java.lang.Character": "str",
    "java.lang.Object": "object", "java.lang.Void": "None",
    "java.lang.Number": "float",
}

COLLECTION_LIST = {"java.util.List", "java.util.ArrayList", "java.util.Collection",
                    "java.util.Iterable", "java.util.Queue", "java.util.Deque",
                    "java.util.LinkedList"}
COLLECTION_SET = {"java.util.Set", "java.util.HashSet", "java.util.TreeSet",
                   "java.util.SortedSet", "java.util.LinkedHashSet"}
COLLECTION_MAP = {"java.util.Map", "java.util.HashMap", "java.util.TreeMap",
                   "java.util.SortedMap", "java.util.LinkedHashMap"}


@dataclass
class RenderContext:
    """Shared across all type renders within one output module file."""
    classes: dict
    module_of: dict  # fqn -> owning python module (None if not stubbed)
    current_module: str
    type_checking_imports: dict = field(default_factory=dict)  # module -> set(names)
    runtime_imports: dict = field(default_factory=dict)  # module -> set(names)
    typevars_seen: dict = field(default_factory=dict)  # name -> bound type string or None

    def _record_import(self, module: str, name: str, runtime: bool) -> None:
        if module == self.current_module:
            return
        bucket = self.runtime_imports if runtime else self.type_checking_imports
        bucket.setdefault(module, set()).add(name)

    def top_level_path(self, fqn: str) -> tuple[str, list[str]] | None:
        """Returns (owning_module, [TopSimple, ..., ThisSimple]) or None if
        `fqn` isn't a stubbed class."""
        c = self.classes.get(fqn)
        if c is None:
            return None
        path = [c["simpleName"]]
        cur = c["outer"]
        module = c["module"]
        while cur:
            cc = self.classes.get(cur)
            if cc is None:
                return None
            path.append(cc["simpleName"])
            module = cc["module"] or module
            cur = cc["outer"]
        if module is None:
            return None
        path.reverse()
        return module, path

    def render(self, type_str: str, runtime: bool = False) -> str:
        return self._render_node(parse_type_str(type_str), runtime)

    def _render_node(self, node: TypeNode, runtime: bool) -> str:
        if node.array_dims > 0:
            inner = TypeNode(node.base, node.args, 0)
            expr = self._render_node(inner, runtime)
            for _ in range(node.array_dims):
                expr = f"list[{expr}]"
            return expr

        base = node.base
        if "." not in base:
            if base in PRIMITIVE_MAP:
                return PRIMITIVE_MAP[base]
            # Any dot-free multi-char base that isn't a primitive is, by
            # construction of resolve.py, a bare Java type variable.
            self.typevars_seen.setdefault(base, None)
            return base

        if base in JAVA_LANG_MAP:
            return JAVA_LANG_MAP[base]
        if base == "java.lang.Class":
            inner = self._render_node(node.args[0], runtime) if node.args else "object"
            return f"type[{inner}]"
        if base in COLLECTION_LIST:
            inner = self._render_node(node.args[0], runtime) if node.args else "object"
            return f"list[{inner}]"
        if base in COLLECTION_SET:
            inner = self._render_node(node.args[0], runtime) if node.args else "object"
            return f"set[{inner}]"
        if base in COLLECTION_MAP:
            if len(node.args) == 2:
                k = self._render_node(node.args[0], runtime)
                v = self._render_node(node.args[1], runtime)
            else:
                k, v = "object", "object"
            return f"dict[{k}, {v}]"

        resolved = self.top_level_path(base)
        if resolved is None:
            return "Any"
        owning_module, path = resolved
        self._record_import(owning_module, path[0], runtime)
        expr = ".".join(path)

        c = self.classes.get(base)
        if node.args and c and c.get("typeParams"):
            arg_strs = [self._render_node(a, runtime) for a in node.args]
            expr += f"[{', '.join(arg_strs)}]"
        return expr
