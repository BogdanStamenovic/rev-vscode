"""Java type model: parsing the type strings in the SDK database, and the
handful of assignability rules the translator needs to pick overloads and
declare locals. javac on the hub is the real type checker; this only has to be
right where the emitted Java text depends on a type."""

from __future__ import annotations

from dataclasses import dataclass, field

PRIMITIVES = ("boolean", "byte", "short", "char", "int", "long", "float", "double", "void")
NUMERIC_RANK = {"byte": 1, "short": 2, "char": 2, "int": 3, "long": 4, "float": 5, "double": 6}
BOXES = {
    "boolean": "java.lang.Boolean", "byte": "java.lang.Byte", "short": "java.lang.Short",
    "char": "java.lang.Character", "int": "java.lang.Integer", "long": "java.lang.Long",
    "float": "java.lang.Float", "double": "java.lang.Double",
}
UNBOXES = {v: k for k, v in BOXES.items()}


@dataclass(frozen=True)
class JType:
    name: str  # primitive, FQN, type variable, or "?" for unknown
    args: tuple[JType, ...] = field(default=())
    dims: int = 0

    @property
    def is_unknown(self) -> bool:
        return self.name == "?"

    @property
    def is_primitive(self) -> bool:
        return self.dims == 0 and self.name in PRIMITIVES

    @property
    def is_numeric(self) -> bool:
        t = self.unboxed()
        return t.dims == 0 and t.name in NUMERIC_RANK

    @property
    def is_integral(self) -> bool:
        t = self.unboxed()
        return t.dims == 0 and t.name in ("byte", "short", "char", "int", "long")

    @property
    def is_string(self) -> bool:
        return self.dims == 0 and self.name == "java.lang.String"

    @property
    def is_array(self) -> bool:
        return self.dims > 0

    @property
    def simple(self) -> str:
        return self.name.rsplit(".", 1)[-1]

    def element(self) -> JType:
        if self.dims:
            return JType(self.name, self.args, self.dims - 1)
        return self.args[0] if self.args else UNKNOWN

    def unboxed(self) -> JType:
        if self.dims == 0 and self.name in UNBOXES:
            return JType(UNBOXES[self.name])
        return self

    def boxed(self) -> JType:
        if self.dims == 0 and self.name in BOXES:
            return JType(BOXES[self.name])
        return self

    def erasure(self) -> JType:
        return JType(self.name, (), self.dims)

    def __str__(self) -> str:
        s = self.name
        if self.args:
            s += "<" + ", ".join(str(a) for a in self.args) + ">"
        return s + "[]" * self.dims


UNKNOWN = JType("?")
VOID = JType("void")
BOOLEAN = JType("boolean")
INT = JType("int")
LONG = JType("long")
DOUBLE = JType("double")
STRING = JType("java.lang.String")
OBJECT = JType("java.lang.Object")
NULL = JType("null")


def parse_type(text: str) -> JType:
    """Parse `java.util.List<com.x.Y>[]`-style strings. Wildcards and bounds
    (`? extends X`) collapse to their bound because nothing downstream needs
    variance."""
    t, rest = _parse(text.strip())
    if rest.strip():
        raise ValueError(f"trailing text in type {text!r}: {rest!r}")
    return t


def _parse(s: str) -> tuple[JType, str]:
    s = s.lstrip()
    if s.startswith("?"):
        s = s[1:].lstrip()
        for kw in ("extends", "super"):
            if s.startswith(kw):
                t, rest = _parse(s[len(kw):])
                return (t if kw == "extends" else OBJECT), rest
        return OBJECT, s
    i = 0
    while i < len(s) and (s[i].isalnum() or s[i] in "._$"):
        i += 1
    name, s = s[:i], s[i:].lstrip()
    if not name:
        raise ValueError(f"expected type name at {s!r}")
    # `T extends Foo` appears in method typeParams; the bound is irrelevant here.
    if s.startswith("extends "):
        _, s = _parse(s[len("extends "):])
        while s.lstrip().startswith("&"):
            _, s = _parse(s.lstrip()[1:])
    args: list[JType] = []
    if s.startswith("<"):
        s = s[1:]
        while True:
            a, s = _parse(s)
            args.append(a)
            s = s.lstrip()
            if s.startswith(","):
                s = s[1:]
                continue
            if s.startswith(">"):
                s = s[1:]
                break
            raise ValueError(f"bad generic args near {s!r}")
    dims = 0
    s = s.lstrip()
    while s.startswith("[]") or s.startswith("..."):
        dims += 1
        s = s[2:] if s.startswith("[]") else s[3:]
        s = s.lstrip()
    return JType(name, tuple(args), dims), s


def type_var_name(param: str) -> str:
    """'T extends com.x.HardwareDevice' -> 'T'"""
    return param.split()[0]


def substitute(t: JType, env: dict[str, JType]) -> JType:
    if not env:
        return t
    if t.name in env and not t.args:
        base = env[t.name]
        return JType(base.name, base.args, base.dims + t.dims)
    if t.args:
        return JType(t.name, tuple(substitute(a, env) for a in t.args), t.dims)
    return t


def numeric_promote(a: JType, b: JType) -> JType:
    """Binary numeric promotion (JLS 5.6.2)."""
    ra = NUMERIC_RANK.get(a.unboxed().name, 0)
    rb = NUMERIC_RANK.get(b.unboxed().name, 0)
    r = max(ra, rb, NUMERIC_RANK["int"])
    return JType({3: "int", 4: "long", 5: "float", 6: "double"}[r])


def local_type(t: JType) -> JType:
    """Type to declare a local with. Java `float` values (e.g. gamepad sticks)
    are declared `double` because Python has one float type and later
    assignments of double expressions to a float local would not compile."""
    t = t.unboxed()
    if t.dims == 0 and t.name == "float":
        return DOUBLE
    if t.dims == 0 and t.name in ("byte", "short", "char"):
        return INT
    return t
