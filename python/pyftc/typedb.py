"""Read access to the SDK type database (docs/ARCHITECTURE.md, contract 1),
plus a minimal hand-written slice of the JDK and the user's own classes, all in
the same shape so lookups do not care where a class came from."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .jtypes import JType, UNKNOWN, parse_type, substitute, type_var_name

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_SDK = "11.2.0"


def _m(name: str, params: list[tuple[str, str]], returns: str, static: bool = False,
       type_params: list[str] | None = None) -> dict[str, Any]:
    return {
        "name": name, "static": static, "abstract": False, "typeParams": type_params or [],
        "params": [{"name": n, "type": t, "varargs": False} for n, t in params],
        "returns": returns, "doc": "",
    }


def _cls(fqn: str, kind: str = "class", type_params: list[str] | None = None,
         extends: list[str] | None = None, methods: list[dict[str, Any]] | None = None,
         fields: list[dict[str, Any]] | None = None, ctors: list[list[tuple[str, str]]] | None = None) -> dict[str, Any]:
    return {
        "kind": kind, "simpleName": fqn.rsplit(".", 1)[-1], "outer": None, "module": None,
        "typeParams": type_params or [], "extends": extends or [], "abstract": False,
        "methods": methods or [], "fields": fields or [], "enumConstants": [], "doc": "",
        "constructors": [{"params": [{"name": n, "type": t, "varargs": False} for n, t in c], "doc": ""}
                         for c in (ctors or [])],
    }


def _math() -> dict[str, Any]:
    d = "double"
    one = ["sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "exp", "log", "log10",
           "toRadians", "toDegrees", "floor", "ceil", "cbrt", "signum"]
    methods = [_m(n, [("a", d)], d, static=True) for n in one]
    methods += [_m(n, [("a", d), ("b", d)], d, static=True) for n in ("atan2", "pow", "hypot", "copySign", "IEEEremainder")]
    for t in ("int", "long", "double"):
        methods += [_m(n, [("a", t), ("b", t)], t, static=True) for n in ("min", "max")]
        methods.append(_m("abs", [("a", t)], t, static=True))
    methods += [_m("round", [("a", d)], "long", static=True),
                _m("floorDiv", [("a", "int"), ("b", "int")], "int", static=True),
                _m("floorMod", [("a", "int"), ("b", "int")], "int", static=True),
                _m("floorDiv", [("a", "long"), ("b", "long")], "long", static=True),
                _m("floorMod", [("a", "long"), ("b", "long")], "long", static=True),
                _m("random", [], d, static=True)]
    fields = [{"name": n, "type": d, "static": True, "final": True, "doc": ""} for n in ("PI", "E")]
    return _cls("java.lang.Math", methods=methods, fields=fields)


JDK: dict[str, dict[str, Any]] = {
    "java.lang.Object": _cls("java.lang.Object", methods=[
        _m("equals", [("o", "java.lang.Object")], "boolean"), _m("hashCode", [], "int"),
        _m("toString", [], "java.lang.String")]),
    "java.lang.String": _cls("java.lang.String", methods=[
        _m("length", [], "int"), _m("isEmpty", [], "boolean"), _m("charAt", [("i", "int")], "char"),
        _m("substring", [("a", "int")], "java.lang.String"),
        _m("substring", [("a", "int"), ("b", "int")], "java.lang.String"),
        _m("contains", [("s", "java.lang.CharSequence")], "boolean"),
        _m("startsWith", [("s", "java.lang.String")], "boolean"),
        _m("endsWith", [("s", "java.lang.String")], "boolean"),
        _m("indexOf", [("s", "java.lang.String")], "int"),
        _m("toUpperCase", [], "java.lang.String"), _m("toLowerCase", [], "java.lang.String"),
        _m("trim", [], "java.lang.String"),
        _m("replace", [("a", "java.lang.CharSequence"), ("b", "java.lang.CharSequence")], "java.lang.String"),
        _m("split", [("regex", "java.lang.String")], "java.lang.String[]"),
        _m("format", [("fmt", "java.lang.String"), ("args", "java.lang.Object...")], "java.lang.String", static=True),
        _m("valueOf", [("o", "java.lang.Object")], "java.lang.String", static=True),
        _m("join", [("sep", "java.lang.CharSequence"), ("parts", "java.lang.Iterable<? extends java.lang.CharSequence>")],
           "java.lang.String", static=True)]),
    "java.lang.Math": _math(),
    "java.lang.Integer": _cls("java.lang.Integer", methods=[
        _m("parseInt", [("s", "java.lang.String")], "int", static=True)],
        fields=[{"name": "MAX_VALUE", "type": "int", "static": True, "final": True, "doc": ""},
                {"name": "MIN_VALUE", "type": "int", "static": True, "final": True, "doc": ""}]),
    "java.lang.Double": _cls("java.lang.Double", methods=[
        _m("parseDouble", [("s", "java.lang.String")], "double", static=True),
        _m("isNaN", [("d", "double")], "boolean", static=True)]),
    "java.lang.Boolean": _cls("java.lang.Boolean"),
    "java.lang.Long": _cls("java.lang.Long"),
    "java.lang.System": _cls("java.lang.System", methods=[
        _m("currentTimeMillis", [], "long", static=True), _m("nanoTime", [], "long", static=True)]),
    "java.lang.Iterable": _cls("java.lang.Iterable", "interface", ["T"]),
    "java.util.Collection": _cls("java.util.Collection", "interface", ["E"], ["java.lang.Iterable<E>"], methods=[
        _m("size", [], "int"), _m("isEmpty", [], "boolean"), _m("contains", [("o", "java.lang.Object")], "boolean"),
        _m("add", [("e", "E")], "boolean"), _m("clear", [], "void")]),
    "java.util.List": _cls("java.util.List", "interface", ["E"], ["java.util.Collection<E>"], methods=[
        _m("get", [("i", "int")], "E"), _m("set", [("i", "int"), ("e", "E")], "E"),
        _m("add", [("i", "int"), ("e", "E")], "void"), _m("remove", [("i", "int")], "E"),
        _m("indexOf", [("o", "java.lang.Object")], "int")]),
    "java.util.ArrayList": _cls("java.util.ArrayList", "class", ["E"], ["java.util.List<E>"], ctors=[[]]),
    "java.util.Map": _cls("java.util.Map", "interface", ["K", "V"], methods=[
        _m("get", [("k", "java.lang.Object")], "V"), _m("put", [("k", "K"), ("v", "V")], "V"),
        _m("containsKey", [("k", "java.lang.Object")], "boolean"), _m("remove", [("k", "java.lang.Object")], "V"),
        _m("size", [], "int"), _m("isEmpty", [], "boolean"), _m("keySet", [], "java.util.Set<K>"),
        _m("values", [], "java.util.Collection<V>"), _m("clear", [], "void")]),
    "java.util.HashMap": _cls("java.util.HashMap", "class", ["K", "V"], ["java.util.Map<K, V>"], ctors=[[]]),
    "java.util.Set": _cls("java.util.Set", "interface", ["E"], ["java.util.Collection<E>"]),
    "java.util.Arrays": _cls("java.util.Arrays", methods=[
        _m("asList", [("a", "T...")], "java.util.List<T>", static=True, type_params=["T"])]),
    "java.lang.Exception": _cls("java.lang.Exception", methods=[_m("getMessage", [], "java.lang.String")]),
    "java.lang.RuntimeException": _cls("java.lang.RuntimeException", extends=["java.lang.Exception"],
                                       ctors=[[], [("msg", "java.lang.String")]]),
    "java.lang.IllegalStateException": _cls("java.lang.IllegalStateException", extends=["java.lang.RuntimeException"],
                                            ctors=[[], [("msg", "java.lang.String")]]),
}


@dataclass
class Member:
    owner: str          # FQN of the declaring class
    data: dict[str, Any]
    env: dict[str, JType]  # class type-variable bindings seen from the receiver

    def param_types(self) -> list[JType]:
        return [substitute(parse_type(p["type"]), self.env) for p in self.data["params"]]

    def return_type(self) -> JType:
        return substitute(parse_type(self.data["returns"]), self.env)

    @property
    def varargs(self) -> bool:
        ps = self.data["params"]
        return bool(ps) and (ps[-1].get("varargs") or ps[-1]["type"].endswith("..."))


class TypeDB:
    def __init__(self, sdk: dict[str, Any]):
        self.sdk_version: str = sdk.get("sdkVersion", "?")
        self.classes: dict[str, dict[str, Any]] = dict(JDK)
        self.classes.update(sdk.get("classes", {}))
        self.xml_tags: dict[str, dict[str, Any]] = sdk.get("xmlTags", {})
        self._by_module: dict[str, dict[str, str]] = {}
        for fqn, c in self.classes.items():
            if c.get("module") and not c.get("outer"):
                self._by_module.setdefault(c["module"], {})[c["simpleName"]] = fqn

    @classmethod
    def load(cls, sdk_version: str = DEFAULT_SDK, path: Path | None = None) -> TypeDB:
        return _load(str(path or DATA_DIR / f"sdk-{sdk_version}.json"))

    def add_class(self, fqn: str, data: dict[str, Any]) -> None:
        self.classes[fqn] = data

    def module_export(self, module: str, name: str) -> str | None:
        if module == "ftc.gamepad" and name == "Gamepad":
            return self.module_export("ftc.hardware", name) or "com.qualcomm.robotcore.hardware.Gamepad"
        return self._by_module.get(module, {}).get(name)

    def module_names(self, module: str) -> dict[str, str]:
        return self._by_module.get(module, {})

    def get(self, fqn: str) -> dict[str, Any] | None:
        return self.classes.get(fqn)

    def nested(self, outer: str, name: str) -> str | None:
        fqn = f"{outer}.{name}"
        if fqn in self.classes:
            return fqn
        for sup in self.supertypes(JType(outer)):
            fqn = f"{sup.name}.{name}"
            if fqn in self.classes:
                return fqn
        return None

    def supertypes(self, t: JType) -> list[JType]:
        """All supertypes, breadth-first, with type arguments substituted."""
        out: list[JType] = []
        seen: set[str] = set()
        queue = [t]
        while queue:
            cur = queue.pop(0)
            c = self.classes.get(cur.name)
            if c is None:
                continue
            env = self._env(c, cur)
            for e in c.get("extends", []):
                try:
                    st = substitute(parse_type(e), env)
                except ValueError:
                    continue
                if st.name not in seen:
                    seen.add(st.name)
                    out.append(st)
                    queue.append(st)
        if t.name != "java.lang.Object" and "java.lang.Object" not in seen:
            out.append(JType("java.lang.Object"))
        return out

    @staticmethod
    def _env(c: dict[str, Any], t: JType) -> dict[str, JType]:
        names = [type_var_name(p) for p in c.get("typeParams", [])]
        return {n: a for n, a in zip(names, t.args)} if len(names) == len(t.args) else {}

    def _walk(self, t: JType) -> list[tuple[str, dict[str, Any], dict[str, JType]]]:
        chain = []
        for cur in [t, *self.supertypes(t)]:
            c = self.classes.get(cur.name)
            if c is not None:
                chain.append((cur.name, c, self._env(c, cur)))
        return chain

    def methods(self, t: JType, name: str) -> list[Member]:
        out: list[Member] = []
        sigs: set[tuple[str, ...]] = set()
        for owner, c, env in self._walk(t):
            for m in c.get("methods", []):
                if m["name"] != name:
                    continue
                sig = tuple(p["type"] for p in m["params"])
                if sig in sigs:  # overridden further down the chain
                    continue
                sigs.add(sig)
                out.append(Member(owner, m, env))
        return out

    def field(self, t: JType, name: str) -> Member | None:
        for owner, c, env in self._walk(t):
            for f in c.get("fields", []):
                if f["name"] == name:
                    return Member(owner, {**f, "params": [], "returns": f["type"]}, env)
        return None

    def constructors(self, fqn: str) -> list[Member]:
        c = self.classes.get(fqn)
        if c is None:
            return []
        return [Member(fqn, {**k, "name": "<init>", "returns": "void", "static": False, "typeParams": []}, {})
                for k in c.get("constructors", [])]

    def is_subtype(self, sub: JType, sup: JType) -> bool | None:
        """True/False when known, None when the DB can't tell (unknown JDK type)."""
        if sub.name == sup.name and sub.dims == sup.dims:
            return True
        if sup.name == "java.lang.Object" and not sub.is_primitive:
            return True
        if sub.dims or sup.dims:
            return False
        if sub.name not in self.classes:
            return None
        return any(s.name == sup.name for s in self.supertypes(sub))

    def is_functional_interface(self, fqn: str) -> bool:
        c = self.classes.get(fqn)
        if not c or c.get("kind") != "interface":
            return False
        return sum(1 for m in c.get("methods", []) if m.get("abstract") and not m.get("static")) == 1


@lru_cache(maxsize=4)
def _load(path: str) -> TypeDB:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"type database not found: {p} (run sdkgen)")
    return TypeDB(json.loads(p.read_text()))
