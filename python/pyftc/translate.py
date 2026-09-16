"""Python subset -> Java 8 source for OnBot Java.

Pipeline per project:
  1. parse every .py file, register each top-level class name
  2. build class signatures (fields, methods, bases) into the TypeDB so user
     classes resolve exactly like SDK classes
  3. translate method bodies; each body is walked three times: two passes to
     settle local variable types (a local first assigned `0` and later `0.5`
     must be declared double), one pass that emits

Unsupported Python is a diagnostic on the offending node, never a guess.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .jtypes import (
    BOOLEAN, DOUBLE, INT, LONG, NULL, OBJECT, STRING, UNKNOWN, VOID, JType,
    local_type, numeric_promote, parse_type, substitute, type_var_name,
)
from .typedb import Member, TypeDB

PACKAGE = "org.firstinspires.ftc.teamcode.pyftc"
HUB_DIR = "/src/" + PACKAGE.replace(".", "/")

JAVA_KEYWORDS = set("""abstract assert boolean break byte case catch char class const continue default do
double else enum extends final finally float for goto if implements import instanceof int interface long
native new package private protected public return short static strictfp super switch synchronized this
throw throws transient try void volatile while true false null var""".split())

PY_EXCEPTIONS = {
    "Exception": "java.lang.RuntimeException", "RuntimeError": "java.lang.RuntimeException",
    "ValueError": "java.lang.IllegalArgumentException", "TypeError": "java.lang.IllegalArgumentException",
    "NotImplementedError": "java.lang.UnsupportedOperationException",
}
CATCH_EXCEPTIONS = {
    "Exception": "java.lang.Exception", "BaseException": "java.lang.Throwable",
    "RuntimeError": "java.lang.RuntimeException", "ValueError": "java.lang.IllegalArgumentException",
    "TypeError": "java.lang.IllegalArgumentException", "IndexError": "java.lang.IndexOutOfBoundsException",
    "ZeroDivisionError": "java.lang.ArithmeticException",
}

# Python method names on builtin containers -> Java. Only applied when the
# receiver is known to be that Java type.
LIST_METHODS = {"append": "add", "extend": "addAll", "insert": "add", "clear": "clear", "index": "indexOf", "remove": "remove"}
STR_METHODS = {"upper": "toUpperCase", "lower": "toLowerCase", "strip": "trim", "startswith": "startsWith",
               "endswith": "endsWith", "find": "indexOf", "replace": "replace", "split": "split"}
MATH_FUNCS = {"sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "exp", "log10", "hypot", "pow"}
MATH_RENAMED = {"radians": "toRadians", "degrees": "toDegrees", "copysign": "copySign", "fabs": "abs"}
MATH_CONSTS = {"pi": "PI", "e": "E", "inf": "Double.POSITIVE_INFINITY", "nan": "Double.NaN", "tau": "(2 * Math.PI)"}

PREC_TERNARY, PREC_OR, PREC_AND, PREC_BITOR, PREC_BITXOR, PREC_BITAND = 1, 2, 3, 4, 5, 6
PREC_EQ, PREC_REL, PREC_SHIFT, PREC_ADD, PREC_MUL, PREC_UNARY, PREC_ATOM = 7, 8, 9, 10, 11, 12, 14


@dataclass
class Diagnostic:
    source: str
    line: int
    col: int
    endLine: int
    endCol: int
    severity: str
    message: str

    def to_json(self) -> dict[str, Any]:
        return self.__dict__.copy()


class Unsupported(Exception):
    def __init__(self, node: ast.AST, message: str):
        super().__init__(message)
        self.node = node
        self.message = message


@dataclass
class ClassRef:
    """An expression that names a class rather than a value."""
    fqn: str


@dataclass
class Expr:
    code: str
    type: JType
    prec: int = PREC_ATOM
    cls: ClassRef | None = None


@dataclass
class PyClass:
    node: ast.ClassDef
    file: PyFile
    fqn: str
    fields: dict[str, JType] = field(default_factory=dict)
    field_nodes: dict[str, ast.AST] = field(default_factory=dict)
    static_fields: set[str] = field(default_factory=set)
    final_fields: set[str] = field(default_factory=set)
    field_inits: dict[str, ast.expr] = field(default_factory=dict)
    superclass: JType | None = None
    interfaces: list[JType] = field(default_factory=list)


@dataclass
class PyFile:
    path: Path
    source: str
    tree: ast.Module | None
    names: dict[str, Any] = field(default_factory=dict)  # python name -> ClassRef | "math" | JType alias
    comments: dict[int, tuple[str, bool]] = field(default_factory=dict)  # line -> (text, trailing)
    classes: list[PyClass] = field(default_factory=list)


class Emitter:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.line_map: list[int] = []
        self.indent = 0

    def emit(self, text: str, pyline: int = 0) -> None:
        self.lines.append(("    " * self.indent + text) if text else "")
        self.line_map.append(pyline)


class ProjectTranslator:
    def __init__(self, db: TypeDB):
        self.db = db
        self.diags: list[Diagnostic] = []
        self.files: list[PyFile] = []
        self.classes: dict[str, PyClass] = {}

    # ---------------------------------------------------------------- driver

    def translate(self, paths: Iterable[Path]) -> dict[str, Any]:
        for p in paths:
            self._parse_file(p)
        for f in self.files:
            self._resolve_imports(f)
        for c in self.classes.values():
            self._guard(c.file, lambda c=c: self._build_signature(c))
        out = []
        for f in self.files:
            for c in f.classes:
                before = len(self.diags)
                java, line_map = ClassTranslator(self, c).run()
                out.append({
                    "source": str(f.path), "className": c.node.name,
                    "hubPath": f"{HUB_DIR}/{c.node.name}.java", "java": java, "lineMap": line_map,
                    "diagnostics": [d.to_json() for d in self.diags[before:]],
                })
        ok = not any(d.severity == "error" for d in self.diags)
        return {"ok": ok, "files": out, "diagnostics": [d.to_json() for d in self.diags]}

    def diag(self, f: PyFile, node: ast.AST | None, message: str, severity: str = "error") -> None:
        line = getattr(node, "lineno", 1) or 1
        col = getattr(node, "col_offset", 0) or 0
        self.diags.append(Diagnostic(
            str(f.path), line, col, getattr(node, "end_lineno", None) or line,
            getattr(node, "end_col_offset", None) or col + 1, severity, message))

    def _guard(self, f: PyFile, fn: Any) -> Any:
        try:
            return fn()
        except Unsupported as e:
            self.diag(f, e.node, e.message)
            return None

    def _parse_file(self, path: Path) -> None:
        source = path.read_text()
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as e:
            f = PyFile(path, source, None)
            self.files.append(f)
            self.diags.append(Diagnostic(str(path), e.lineno or 1, max((e.offset or 1) - 1, 0), e.lineno or 1,
                                         e.offset or 1, "error", f"syntax error: {e.msg}"))
            return
        f = PyFile(path, source, tree, comments=_comments(source))
        self.files.append(f)
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                if node.name in self.classes:
                    self.diag(f, node, f"class {node.name} is also defined in {self.classes[node.name].file.path.name}; "
                                       "all classes share one Java package, names must be unique")
                    continue
                if node.name in JAVA_KEYWORDS:
                    self.diag(f, node, f"'{node.name}' is a Java keyword and cannot be a class name")
                    continue
                c = PyClass(node, f, f"{PACKAGE}.{node.name}")
                f.classes.append(c)
                self.classes[node.name] = c
                self.db.add_class(c.fqn, {"kind": "class", "simpleName": node.name, "outer": None, "module": None,
                                          "typeParams": [], "extends": [], "abstract": False, "methods": [],
                                          "fields": [], "enumConstants": [], "constructors": [], "doc": ""})

    def _resolve_imports(self, f: PyFile) -> None:
        if f.tree is None:
            return
        for c in f.classes:
            f.names[c.node.name] = ClassRef(c.fqn)
        for node in f.tree.body:
            if isinstance(node, ast.ClassDef):
                continue
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod == "__future__" or mod == "typing":
                    continue
                for alias in node.names:
                    local = alias.asname or alias.name
                    if alias.name == "*":
                        self.diag(f, node, "wildcard imports are not supported; import names explicitly")
                    elif mod == "ftc.lang":
                        alias_t = {"long": "long", "short": "short", "byte": "byte", "char": "char", "float32": "float"}.get(alias.name)
                        if alias_t is None:
                            self.diag(f, node, f"ftc.lang has no '{alias.name}'")
                        else:
                            f.names[local] = JType(alias_t)
                    elif mod.startswith("ftc."):
                        fqn = self.db.module_export(mod, alias.name)
                        if fqn is None:
                            self.diag(f, node, f"{mod} has no '{alias.name}' in SDK {self.db.sdk_version}")
                        else:
                            f.names[local] = ClassRef(fqn)
                    elif mod == "math":
                        f.names[local] = ("mathattr", alias.name)
                    elif alias.name in self.classes and mod.lstrip(".").split(".")[-1] == self.classes[alias.name].file.path.stem:
                        f.names[local] = ClassRef(self.classes[alias.name].fqn)
                    else:
                        self.diag(f, node, f"cannot import '{alias.name}' from '{mod}': only ftc.*, math, "
                                           "and classes from other files in this project are available on the robot")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "math":
                        f.names[alias.asname or "math"] = "math"
                    else:
                        self.diag(f, node, f"module '{alias.name}' is not available on the robot "
                                           "(use 'from ftc.<module> import Name')")
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                continue  # module docstring
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.diag(f, node, "module-level functions are not supported: Java has no free functions. "
                                   "Put it in a class as a @staticmethod")
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                self.diag(f, node, "module-level variables are not supported: Java has no globals. "
                                   "Make it a class attribute (UPPER_CASE names become static final constants)")
            elif isinstance(node, ast.If) and _is_main_guard(node):
                self.diag(f, node, "`if __name__ == '__main__'` code never runs on the robot and is skipped", "warning")
            else:
                self.diag(f, node, f"unsupported top-level statement ({type(node).__name__})")

    # ------------------------------------------------------------ signatures

    def resolve_annotation(self, f: PyFile, node: ast.expr | None) -> JType:
        if node is None:
            return UNKNOWN
        if isinstance(node, ast.Constant):
            if node.value is None:
                return VOID
            if isinstance(node.value, str):
                return self.resolve_annotation(f, ast.parse(node.value, mode="eval").body)
        if isinstance(node, ast.Name):
            builtin = {"float": DOUBLE, "int": INT, "bool": BOOLEAN, "str": STRING, "object": OBJECT}.get(node.id)
            bound = f.names.get(node.id)
            if isinstance(bound, JType):
                return bound
            if isinstance(bound, ClassRef):
                return JType(bound.fqn)
            if builtin is not None:
                return builtin
            if node.id in ("list", "dict"):
                raise Unsupported(node, f"write {node.id}[...] with element types, e.g. list[float]")
            raise Unsupported(node, f"unknown type '{node.id}' (did you forget an import?)")
        if isinstance(node, ast.Attribute):
            outer = self.resolve_annotation(f, node.value)
            nested = self.db.nested(outer.name, node.attr)
            if nested is None:
                raise Unsupported(node, f"{outer.simple} has no nested type '{node.attr}'")
            return JType(nested)
        if isinstance(node, ast.Subscript):
            base = node.value.id if isinstance(node.value, ast.Name) else None
            items = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
            if base == "list" and len(items) == 1:
                return JType("java.util.List", (self.resolve_annotation(f, items[0]).boxed(),))
            if base == "dict" and len(items) == 2:
                return JType("java.util.Map", tuple(self.resolve_annotation(f, i).boxed() for i in items))
            if base in ("Optional", "ClassVar", "Final") and len(items) == 1:
                return self.resolve_annotation(f, items[0])
            if base == "type" and len(items) == 1:
                return JType("java.lang.Class", (self.resolve_annotation(f, items[0]),))
            raise Unsupported(node, "unsupported type annotation")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            for a, b in ((node.left, node.right), (node.right, node.left)):
                if isinstance(b, ast.Constant) and b.value is None:
                    return self.resolve_annotation(f, a)
        raise Unsupported(node, "unsupported type annotation")

    def _build_signature(self, c: PyClass) -> None:
        f, node = c.file, c.node
        data = self.db.get(c.fqn)
        assert data is not None
        for b in node.bases:
            t = self.resolve_annotation(f, b)
            kind = (self.db.get(t.name) or {}).get("kind")
            if kind == "interface":
                c.interfaces.append(t)
            elif c.superclass is None:
                c.superclass = t
            else:
                raise Unsupported(b, "Java allows only one superclass")
        data["extends"] = [str(t) for t in ([c.superclass] if c.superclass else []) + c.interfaces]
        if node.keywords:
            raise Unsupported(node, "class keyword arguments are not supported")

        methods = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                name = stmt.target.id
                c.fields[name] = local_type(self.resolve_annotation(f, stmt.annotation))
                c.field_nodes[name] = stmt
                ann_base = stmt.annotation.value if isinstance(stmt.annotation, ast.Subscript) else stmt.annotation
                is_classvar = isinstance(ann_base, ast.Name) and ann_base.id in ("ClassVar", "Final")
                if is_classvar or (stmt.value is not None and name.isupper()):
                    c.static_fields.add(name)
                if stmt.value is not None and (name.isupper() or (isinstance(ann_base, ast.Name) and ann_base.id == "Final")):
                    c.final_fields.add(name)
                if stmt.value is not None:
                    c.field_inits[name] = stmt.value
            elif isinstance(stmt, ast.Assign):
                if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                    raise Unsupported(stmt, "class attributes must be simple `NAME: type = value` assignments")
                name = stmt.targets[0].id
                t = ClassTranslator(self, c).literal_type(stmt.value)
                if t.is_unknown:
                    raise Unsupported(stmt, f"add a type annotation: `{name}: <type> = ...`")
                c.fields[name] = local_type(t)
                c.field_nodes[name] = stmt
                c.field_inits[name] = stmt.value
                if name.isupper():
                    c.static_fields.add(name)
                    c.final_fields.add(name)
            elif isinstance(stmt, ast.FunctionDef):
                methods.append(stmt)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            elif isinstance(stmt, ast.Pass):
                continue
            else:
                self.diag(f, stmt, f"unsupported statement in class body ({type(stmt).__name__})")

        # `self.x: T = ...` inside methods also declares a field (common Python style)
        for m in methods:
            for sub in ast.walk(m):
                if (isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Attribute)
                        and isinstance(sub.target.value, ast.Name) and sub.target.value.id == "self"):
                    name = sub.target.attr
                    t = local_type(self.resolve_annotation(f, sub.annotation))
                    if name in c.fields and c.fields[name] != t:
                        self.diag(f, sub, f"field '{name}' already declared as {c.fields[name]}")
                    c.fields.setdefault(name, t)
                    c.field_nodes.setdefault(name, sub)

        data["fields"] = [{"name": n, "type": str(t), "static": n in c.static_fields, "final": n in c.final_fields, "doc": ""}
                          for n, t in c.fields.items()]
        ctors, meths = [], []
        for m in methods:
            sig = self._guard(f, lambda m=m: self._method_signature(c, m))
            if sig is None:
                continue
            (ctors if m.name == "__init__" else meths).append(sig)
        data["methods"] = meths
        data["constructors"] = ctors or [{"params": [], "doc": ""}]

        # unannotated `self.x = expr` in any method: infer from the expression once signatures exist
        for m in methods:
            for sub in ast.walk(m):
                if isinstance(sub, ast.Assign):
                    for tgt in sub.targets:
                        if (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name)
                                and tgt.value.id == "self" and tgt.attr not in c.fields
                                and self.db.field(JType(c.fqn), tgt.attr) is None):
                            t = self._guard(f, lambda v=sub.value: ClassTranslator(self, c).field_init_type(v))
                            if t is None or t.is_unknown or t == NULL:
                                self.diag(f, sub, f"cannot infer the type of field '{tgt.attr}'; declare it in the "
                                                  f"class body, e.g. `{tgt.attr}: DcMotor`")
                                continue
                            c.fields[tgt.attr] = local_type(t)
                            c.field_nodes[tgt.attr] = sub
                            data["fields"].append({"name": tgt.attr, "type": str(local_type(t)), "static": False,
                                                   "final": False, "doc": ""})

    def _method_signature(self, c: PyClass, m: ast.FunctionDef) -> dict[str, Any]:
        f = c.file
        static = any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in m.decorator_list)
        for d in m.decorator_list:
            if not (isinstance(d, ast.Name) and d.id in ("staticmethod", "override")):
                raise Unsupported(d, "only @staticmethod is supported on methods")
        a = m.args
        if a.vararg or a.kwarg or a.kwonlyargs or a.posonlyargs or a.defaults:
            raise Unsupported(m, "methods may only have plain positional parameters (no defaults, *args, **kwargs)")
        params = list(a.args)
        if not static:
            if not params or params[0].arg != "self":
                raise Unsupported(m, "instance methods must take `self` first (or mark @staticmethod)")
            params = params[1:]
        out_params = []
        for p in params:
            if p.annotation is None:
                raise Unsupported(p, f"parameter '{p.arg}' needs a type annotation (Java needs the type)")
            out_params.append({"name": _ident(p.arg), "type": str(local_type(self.resolve_annotation(f, p.annotation))),
                               "varargs": False})
        if m.name == "__init__":
            return {"params": out_params, "doc": "", "static": False}
        if m.returns is not None:
            ret = self.resolve_annotation(f, m.returns)
            ret = local_type(ret) if not ret.is_unknown else ret
        elif any(isinstance(n, ast.Return) and n.value is not None for n in _walk_function(m)):
            raise Unsupported(m, f"method '{m.name}' returns a value; add a return annotation (-> float, ...)")
        else:
            ret = VOID
        if m.name.startswith("__") and m.name.endswith("__"):
            raise Unsupported(m, f"special method {m.name} has no Java equivalent")
        return {"name": m.name, "static": static, "abstract": False, "typeParams": [], "params": out_params,
                "returns": str(ret), "doc": ""}


# ---------------------------------------------------------------------------

@dataclass
class Scope:
    """Local variables for one method body."""
    params: dict[str, JType]
    types: dict[str, JType] = field(default_factory=dict)
    declared: set[str] = field(default_factory=set)
    loop_vars: set[str] = field(default_factory=set)


@dataclass
class DeclPlan:
    # id(statement) -> vars declared inline at that assignment
    inline: dict[int, set[str]] = field(default_factory=dict)
    # (id(block list), index) -> vars declared with a default right before that statement
    hoist: dict[tuple[int, int], list[str]] = field(default_factory=dict)
    # id(for statement) -> True when the loop target can be the Java loop variable
    loop_scoped: set[int] = field(default_factory=set)


class ClassTranslator:
    def __init__(self, project: ProjectTranslator, c: PyClass):
        self.p = project
        self.db = project.db
        self.c = c
        self.f = c.file
        self.out = Emitter()
        self.imports: dict[str, str] = {}  # simple name -> FQN
        self.scope: Scope | None = None
        self.plan = DeclPlan()
        self.method: ast.FunctionDef | None = None
        self.static_ctx = False
        self.collect = False  # True during type-settling passes: no emission, no diagnostics
        self.comment_cursor = 0
        self.emitted_comments: set[int] = set()
        self.tmp_counter = 0

    # ------------------------------------------------------------ utilities

    def fail(self, node: ast.AST, msg: str) -> Unsupported:
        return Unsupported(node, msg)

    def warn(self, node: ast.AST, msg: str) -> None:
        if not self.collect:
            self.p.diag(self.f, node, msg, "warning")

    def ref(self, fqn: str) -> str:
        """Render a class name, recording the import it needs."""
        data = self.db.get(fqn)
        outer_chain = []
        top = fqn
        while data is not None and data.get("outer"):
            outer_chain.insert(0, data["simpleName"])
            top = data["outer"]
            data = self.db.get(top)
        simple = top.rsplit(".", 1)[-1]
        pkg = top.rsplit(".", 1)[0] if "." in top else ""
        if pkg not in ("java.lang", PACKAGE, ""):
            existing = self.imports.get(simple)
            if existing is None:
                self.imports[simple] = top
            elif existing != top:
                return ".".join([top, *outer_chain])
        return ".".join([simple, *outer_chain])

    def render(self, t: JType) -> str:
        if t.is_unknown:
            return "Object"
        if t.name in ("boolean", "byte", "short", "char", "int", "long", "float", "double", "void") or "." not in t.name:
            base = t.name
        else:
            base = self.ref(t.name)
        if t.args:
            base += "<" + ", ".join(self.render(a.boxed()) for a in t.args) + ">"
        return base + "[]" * t.dims

    def emit(self, text: str, node: ast.AST | None = None) -> None:
        if self.collect:
            return
        line = getattr(node, "lineno", 0) if node is not None else 0
        if line:
            self.flush_comments(line - 1)
        trailing = self.f.comments.get(line) if line else None
        if trailing and trailing[1] and line not in self.emitted_comments and text:
            self.emitted_comments.add(line)
            text = f"{text} // {trailing[0]}"
        self.out.emit(text, line)

    def flush_comments(self, up_to_line: int) -> None:
        if self.collect:
            return
        for ln in sorted(self.f.comments):
            if ln > up_to_line:
                break
            text, trailing = self.f.comments[ln]
            if ln in self.emitted_comments or trailing or ln < self.comment_cursor:
                continue
            self.emitted_comments.add(ln)
            self.out.emit(f"// {text}" if text else "//", ln)

    # ------------------------------------------------------------ class

    def run(self) -> tuple[str, list[int]]:
        node = self.c.node
        body_out = Emitter()
        self.out = body_out
        # comments above the class (after imports) belong to the class
        first_code_line = min([n.lineno for n in self.f.tree.body if not isinstance(n, (ast.Import, ast.ImportFrom))] or [node.lineno])
        self.comment_cursor = first_code_line if node is not self._first_class() else 0
        import_lines = [n.end_lineno or n.lineno for n in self.f.tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        if import_lines and node is self._first_class():
            self.comment_cursor = max(import_lines) + 1
        start_line = min([d.lineno for d in node.decorator_list] + [node.lineno])
        self.flush_comments(start_line - 1)
        self.comment_cursor = start_line

        for d in node.decorator_list:
            self.p._guard(self.f, lambda d=d: self.emit(self.annotation(d), d))
        header = f"public class {node.name}"
        if self.c.superclass:
            header += f" extends {self.render(self.c.superclass)}"
        if self.c.interfaces:
            header += " implements " + ", ".join(self.render(i) for i in self.c.interfaces)
        self.emit(header + " {", node)
        self.out.indent += 1

        for name, t in self.c.fields.items():
            fnode = self.c.field_nodes[name]
            mods = ("static " if name in self.c.static_fields else "") + ("final " if name in self.c.final_fields else "")
            init = self.c.field_inits.get(name)
            if init is not None and isinstance(fnode, (ast.AnnAssign, ast.Assign)) and fnode in self.c.node.body:
                def emit_field(name=name, t=t, init=init, fnode=fnode, mods=mods) -> None:
                    self.static_ctx = name in self.c.static_fields
                    self.scope = Scope({})
                    e = self.coerce(self.expr(init, t), t, init)
                    self.emit(f"{mods}{self.render(t)} {_ident(name)} = {e.code};", fnode)
                self.p._guard(self.f, emit_field)
            else:
                self.emit(f"{mods}{self.render(t)} {_ident(name)};", fnode if fnode in self.c.node.body else None)
        self.static_ctx = False

        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                self.emit("")
                self.p._guard(self.f, lambda s=stmt: self.method_decl(s))
        self.flush_comments(node.end_lineno or node.lineno)
        self.out.indent -= 1
        self.emit("}")

        head = Emitter()
        head.emit(f"package {PACKAGE};")
        head.emit("")
        head.emit(f"// Generated by pyftc from {self.f.path.name}. Edits here are overwritten on the next deploy.")
        head.emit("")
        for simple, fqn in sorted(self.imports.items(), key=lambda kv: kv[1]):
            head.emit(f"import {fqn};")
        if self.imports:
            head.emit("")
        return "\n".join(head.lines + body_out.lines) + "\n", head.line_map + body_out.line_map

    def _first_class(self) -> ast.ClassDef:
        return self.f.classes[0].node

    def annotation(self, d: ast.expr) -> str:
        target = d.func if isinstance(d, ast.Call) else d
        if not isinstance(target, ast.Name):
            raise self.fail(d, "unsupported decorator")
        bound = self.f.names.get(target.id)
        if not isinstance(bound, ClassRef) or (self.db.get(bound.fqn) or {}).get("kind") != "annotation":
            raise self.fail(d, f"'{target.id}' is not a Java annotation (import TeleOp/Autonomous/Disabled from ftc.opmode)")
        text = "@" + self.ref(bound.fqn)
        if isinstance(d, ast.Call):
            if d.args:
                raise self.fail(d, "annotation arguments must be keywords, e.g. @TeleOp(name=\"Drive\")")
            parts = []
            for kw in d.keywords:
                if not isinstance(kw.value, ast.Constant):
                    raise self.fail(kw.value, "annotation values must be literals")
                parts.append(f"{kw.arg} = {_literal(kw.value.value)}")
            text += "(" + ", ".join(parts) + ")"
        return text

    # ------------------------------------------------------------ methods

    def method_decl(self, m: ast.FunctionDef) -> None:
        data = self.db.get(self.c.fqn) or {}
        static = any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in m.decorator_list)
        is_ctor = m.name == "__init__"
        if is_ctor:
            idx = [s for s in self.c.node.body if isinstance(s, ast.FunctionDef) and s.name == "__init__"].index(m)
            sig = data["constructors"][idx]
        else:
            sig = next((s for s in data.get("methods", []) if s["name"] == m.name
                        and len(s["params"]) == len(m.args.args) - (0 if static else 1)), None)
            if sig is None:
                return  # signature failed earlier and was already reported
        params = {p["name"]: parse_type(p["type"]) for p in sig["params"]}
        ret = VOID if is_ctor else parse_type(sig["returns"])

        self.method = m
        self.static_ctx = static
        # settle local types, then emit
        self.plan = self.decl_plan(m)
        types: dict[str, JType] = {}
        for _ in range(2):
            self.collect = True
            self.scope = Scope(dict(params), types=dict(types))
            try:
                self.block(m.body, ret)
            except Unsupported:
                pass
            types = self.scope.types
        self.collect = False
        self.scope = Scope(dict(params), types=types)

        if not is_ctor and self._overrides(m.name, [parse_type(p["type"]) for p in sig["params"]]):
            self.emit("@Override", m)
        param_text = ", ".join(f"{self.render(t)} {n}" for n, t in params.items())
        if is_ctor:
            self.emit(f"public {self.c.node.name}({param_text}) {{", m)
        else:
            self.emit(f"public {'static ' if static else ''}{self.render(ret)} {_ident(m.name)}({param_text}) {{", m)
        self.out.indent += 1
        self.block(m.body, ret)
        self.flush_comments(m.end_lineno or m.lineno)
        self.out.indent -= 1
        self.emit("}")
        self.method = None

    def _overrides(self, name: str, params: list[JType]) -> bool:
        for sup in self.db.supertypes(JType(self.c.fqn)):
            for owner_member in self.db.methods(sup, name):
                if len(owner_member.data["params"]) == len(params):
                    return True
        return False

    # ------------------------------------------------------------ declaration planning

    def decl_plan(self, m: ast.FunctionDef) -> DeclPlan:
        """Decide where each local is declared. Python locals are function
        scoped, Java locals are block scoped. A local is declared at its first
        assignment when every use sits later in that same block (or nested
        inside it); otherwise it is hoisted, with a default value, to the
        smallest block that contains every use."""
        plan = DeclPlan()
        params = {a.arg for a in m.args.args}
        occ: dict[str, list[tuple[tuple[Any, ...], bool, ast.stmt]]] = {}
        blocks: dict[tuple[Any, ...], list[ast.stmt]] = {}

        def names_in(node: ast.AST) -> Iterable[ast.Name]:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name):
                    yield sub

        def walk_block(stmts: list[ast.stmt], path: tuple[Any, ...]) -> None:
            blocks[path] = stmts
            for i, s in enumerate(stmts):
                sp = path + (i,)
                shallow = _shallow_parts(s)
                for part in shallow:
                    for n in names_in(part):
                        occ.setdefault(n.id, []).append((sp, isinstance(n.ctx, ast.Store), s))
                if isinstance(s, ast.For):
                    for n in names_in(s.target):
                        occ.setdefault(n.id, []).append((sp, True, s))
                if isinstance(s, ast.Try):
                    for h_i, h in enumerate(s.handlers):
                        if h.name:
                            occ.setdefault(h.name, []).append((sp + ("handler", h_i), True, s))
                        walk_block(h.body, sp + ("handler", h_i))
                for fname in ("body", "orelse", "finalbody"):
                    sub = getattr(s, fname, None)
                    if isinstance(sub, list) and sub and isinstance(sub[0], ast.stmt):
                        walk_block(sub, sp + (fname,))

        walk_block(m.body, ())
        for name, uses in occ.items():
            if name in params or not any(store for _, store, _ in uses):
                continue
            first = next(u for u in uses if u[1])
            fpath, _, fstmt = first
            if isinstance(fstmt, ast.For) and all(u[0][:len(fpath)] == fpath for u in uses) \
                    and name in {n.id for n in ast.walk(fstmt.target) if isinstance(n, ast.Name)}:
                plan.loop_scoped.add(id(fstmt))
                continue
            if isinstance(fstmt, ast.Try) and len(fpath) >= 2 and fpath[-2] == "handler":
                continue  # `except E as name` is scoped by the catch clause
            block_path, idx = fpath[:-1], fpath[-1]
            inline_ok = (not isinstance(fstmt, ast.For)
                         and all(u[0][:len(block_path)] == block_path and u[0][len(block_path)] >= idx for u in uses)
                         and not _loop_between(uses, fpath))
            if inline_ok:
                plan.inline.setdefault(id(fstmt), set()).add(name)
                continue
            # Paths alternate statement index and block name: (3, "body", 0, "orelse", 1).
            common = _common_prefix([u[0] for u in uses])
            if common in blocks and common:  # all uses inside one except-handler body
                hoist_block, hoist_idx = common, min(u[0][len(common)] for u in uses)
            elif common and isinstance(common[-1], int):
                # Every use is inside one statement. If that statement is itself a
                # block owner, hoist to just before it; its uses span its sub-blocks.
                hoist_block, hoist_idx = common[:-1], common[-1]
            else:
                if common and common[-1] == "handler":
                    common = common[:-1]
                while common and not isinstance(common[-1], int) and common not in blocks:
                    common = common[:-1]
                hoist_block = common if common in blocks else ()
                hoist_idx = min(u[0][len(hoist_block)] for u in uses)
            if hoist_block not in blocks:
                hoist_block, hoist_idx = (), min(u[0][0] for u in uses)
            plan.hoist.setdefault((id(blocks[hoist_block]), hoist_idx), []).append(name)
        return plan

    # ------------------------------------------------------------ statements

    def block(self, stmts: list[ast.stmt], ret: JType) -> None:
        for i, s in enumerate(stmts):
            if i and not self.collect and self._blank_line_between(stmts[i - 1], s):
                self.out.emit("", 0)
            for name in self.plan.hoist.get((id(stmts), i), []):
                if name in self.scope.declared:
                    continue
                t = self.scope.types.get(name, UNKNOWN)
                if t.is_unknown or t == NULL:
                    if not self.collect:
                        self.p.diag(self.f, s, f"cannot infer the type of '{name}'; annotate its first assignment "
                                               f"(e.g. `{name}: float = ...`)")
                    t = OBJECT if t.is_unknown else t
                self.scope.declared.add(name)
                self.emit(f"{self.render(t)} {_ident(name)} = {_default(t)};", s)
            try:
                self.stmt(s, ret)
            except Unsupported as e:
                if not self.collect:
                    self.p.diag(self.f, e.node, e.message)

    def _blank_line_between(self, a: ast.stmt, b: ast.stmt) -> bool:
        lines = self.f.source.splitlines()
        first = min([b.lineno] + [ln for ln in self.f.comments if (a.end_lineno or a.lineno) < ln < b.lineno])
        return any(not lines[ln - 1].strip() for ln in range((a.end_lineno or a.lineno) + 1, first))

    def stmt(self, s: ast.stmt, ret: JType) -> None:
        if isinstance(s, ast.Expr):
            if isinstance(s.value, ast.Constant) and isinstance(s.value.value, str):
                return  # docstring
            if not isinstance(s.value, ast.Call):
                raise self.fail(s, "this expression does nothing (Java only allows calls as statements)")
            self.emit(self.expr(s.value).code + ";", s)
        elif isinstance(s, ast.Assign):
            if len(s.targets) != 1:
                raise self.fail(s, "chained assignment (a = b = x) is not supported")
            self.assign(s, s.targets[0], None, s.value)
        elif isinstance(s, ast.AnnAssign):
            t = local_type(self.p.resolve_annotation(self.f, s.annotation))
            if isinstance(s.target, ast.Name) and s.value is None:
                name = s.target.id
                self.scope.types[name] = t
                if name not in self.scope.declared and not self._hoisted_anywhere(name):
                    self.scope.declared.add(name)
                    self.emit(f"{self.render(t)} {_ident(name)} = {_default(t)};", s)
                return
            if s.value is None:
                return  # `self.x: T` field declaration, already emitted
            self.assign(s, s.target, t, s.value)
        elif isinstance(s, ast.AugAssign):
            self.aug_assign(s)
        elif isinstance(s, ast.If):
            self.if_stmt(s, ret, "if")
        elif isinstance(s, ast.While):
            if s.orelse:
                raise self.fail(s, "while/else is not supported")
            cond = self.condition(s.test)
            if cond.code == "true" and self._in_linear_opmode():
                self.warn(s, "`while True` never checks for STOP; use `while self.opModeIsActive():`")
            self.emit(f"while ({cond.code}) {{", s)
            self.body(s.body, ret)
        elif isinstance(s, ast.For):
            self.for_stmt(s, ret)
        elif isinstance(s, ast.Break):
            self.emit("break;", s)
        elif isinstance(s, ast.Continue):
            self.emit("continue;", s)
        elif isinstance(s, ast.Pass):
            if not self.collect:
                self.flush_comments(s.lineno)
        elif isinstance(s, ast.Return):
            if s.value is None:
                self.emit("return;", s)
            else:
                e = self.coerce(self.expr(s.value, ret), ret, s.value)
                self.emit(f"return {e.code};", s)
        elif isinstance(s, ast.Raise):
            self.raise_stmt(s)
        elif isinstance(s, ast.Try):
            self.try_stmt(s, ret)
        else:
            raise self.fail(s, f"unsupported statement: {type(s).__name__}")

    def body(self, stmts: list[ast.stmt], ret: JType, close: bool = True) -> None:
        saved = set(self.scope.declared)
        self.out.indent += 1
        self.block(stmts, ret)
        if stmts and not self.collect:
            self.flush_comments(stmts[-1].end_lineno or stmts[-1].lineno)
        self.out.indent -= 1
        self.scope.declared = saved
        if close:
            self.emit("}")

    def _hoisted_anywhere(self, name: str) -> bool:
        return any(name in names for names in self.plan.hoist.values())

    def _in_linear_opmode(self) -> bool:
        return self.db.is_subtype(JType(self.c.fqn), JType("com.qualcomm.robotcore.eventloop.opmode.LinearOpMode")) is True

    def assign(self, s: ast.stmt, target: ast.expr, declared: JType | None, value: ast.expr) -> None:
        if isinstance(target, ast.Name):
            name = target.id
            if name in self.scope.params:
                t = self.scope.params[name]
                e = self.coerce(self.expr(value, t), t, value)
                self.emit(f"{_ident(name)} = {e.code};", s)
                return
            known = self.scope.types.get(name)
            e = self.expr(value, declared or known)
            if declared is not None:
                t = declared
            else:
                t = _widen(known, local_type(e.type))
            if self.collect:
                self.scope.types[name] = t if declared is None else declared
                if declared is not None:
                    self.scope.types[name] = declared
            t = self.scope.types.get(name, t)
            e = self.coerce(e, t, value)
            if name not in self.scope.declared and name in self.plan.inline.get(id(s), set()):
                if t.is_unknown or t == NULL:
                    raise self.fail(s, f"cannot infer the type of '{name}'; annotate it (e.g. `{name}: float = ...`)")
                self.scope.declared.add(name)
                self.emit(f"{self.render(t)} {_ident(name)} = {e.code};", s)
            else:
                self.emit(f"{_ident(name)} = {e.code};", s)
        elif isinstance(target, ast.Attribute):
            lhs = self.expr(target)
            e = self.coerce(self.expr(value, lhs.type), lhs.type, value)
            self.emit(f"{lhs.code} = {e.code};", s)
        elif isinstance(target, ast.Subscript):
            obj = self.expr(target.value)
            if isinstance(target.slice, ast.Slice):
                raise self.fail(target, "slice assignment is not supported")
            if obj.type.is_array:
                idx = self.expr(target.slice, INT)
                e = self.coerce(self.expr(value, obj.type.element()), obj.type.element(), value)
                self.emit(f"{_paren(obj, PREC_ATOM)}[{idx.code}] = {e.code};", s)
            elif self._is(obj.type, "java.util.List"):
                idx = self.index_expr(obj, target.slice)
                el = self._type_arg(obj.type, "java.util.List", 0)
                e = self.coerce(self.expr(value, el), el, value)
                self.emit(f"{_paren(obj, PREC_ATOM)}.set({idx}, {e.code});", s)
            elif self._is(obj.type, "java.util.Map"):
                k = self.expr(target.slice, self._type_arg(obj.type, "java.util.Map", 0))
                v = self.expr(value, self._type_arg(obj.type, "java.util.Map", 1))
                self.emit(f"{_paren(obj, PREC_ATOM)}.put({k.code}, {v.code});", s)
            else:
                raise self.fail(target, f"cannot assign by index into {self._show(obj.type)}")
        elif isinstance(target, (ast.Tuple, ast.List)):
            raise self.fail(target, "tuple unpacking is not supported; assign each variable separately")
        else:
            raise self.fail(target, "unsupported assignment target")

    def aug_assign(self, s: ast.AugAssign) -> None:
        op = s.op
        if isinstance(s.target, ast.Subscript):
            # xs[i] += v  ->  xs.set(i, xs.get(i) + v)
            load = ast.copy_location(ast.Subscript(s.target.value, s.target.slice, ast.Load()), s.target)
            value = ast.copy_location(ast.BinOp(load, op, s.value), s)
            self.assign(s, s.target, None, value)
            return
        lhs = self.expr(s.target)
        if isinstance(s.target, ast.Name) and s.target.id not in self.scope.params:
            rhs = self.expr(s.value)
            if self.collect:
                widened = _widen(self.scope.types.get(s.target.id), local_type(self._binop_type(lhs.type, op, rhs.type)))
                self.scope.types[s.target.id] = widened
        rhs = self.expr(s.value)
        simple = {ast.Add: "+=", ast.Sub: "-=", ast.Mult: "*=", ast.BitAnd: "&=", ast.BitOr: "|=",
                  ast.BitXor: "^=", ast.LShift: "<<=", ast.RShift: ">>="}
        if type(op) in simple and not (isinstance(op, ast.Add) and lhs.type.is_string and not rhs.type.is_string and False):
            self.emit(f"{lhs.code} {simple[type(op)]} {rhs.code};", s)
        elif isinstance(op, ast.Div) and not lhs.type.is_integral:
            self.emit(f"{lhs.code} /= {rhs.code};", s)
        else:
            full = self.binop(ast.copy_location(ast.BinOp(s.target, op, s.value), s))
            full = self.coerce(full, lhs.type, s)
            self.emit(f"{lhs.code} = {full.code};", s)

    def if_stmt(self, s: ast.If, ret: JType, keyword: str) -> None:
        cond = self.condition(s.test)
        self.emit(f"{keyword} ({cond.code}) {{", s)
        self.body(s.body, ret, close=False)
        if s.orelse:
            if len(s.orelse) == 1 and isinstance(s.orelse[0], ast.If):
                if not self.collect:
                    self.out.emit("}", s.orelse[0].lineno)
                self._else_if(s.orelse[0], ret)
                return
            self.emit("} else {")
            self.body(s.orelse, ret)
        else:
            self.emit("}")

    def _else_if(self, s: ast.If, ret: JType) -> None:
        # join "}" and "else if (...) {" onto one line
        cond = self.condition(s.test)
        if not self.collect:
            self.out.lines[-1] = self.out.lines[-1] + f" else if ({cond.code}) {{"
            self.out.line_map[-1] = s.lineno
        self.body(s.body, ret, close=False)
        if s.orelse:
            if len(s.orelse) == 1 and isinstance(s.orelse[0], ast.If):
                if not self.collect:
                    self.out.emit("}", s.orelse[0].lineno)
                self._else_if(s.orelse[0], ret)
                return
            self.emit("} else {")
            self.body(s.orelse, ret)
        else:
            self.emit("}")

    def for_stmt(self, s: ast.For, ret: JType) -> None:
        if s.orelse:
            raise self.fail(s, "for/else is not supported")
        loop_scoped = id(s) in self.plan.loop_scoped
        it = s.iter
        if isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == "enumerate":
            self.enumerate_loop(s, ret)
            return
        target = _for_target_name(s)
        if target is None:
            raise self.fail(s.target, "for-loop target must be a single name")
        if isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == "range":
            if it.keywords or not 1 <= len(it.args) <= 3:
                raise self.fail(it, "range() takes 1 to 3 positional arguments")
            args = [self.coerce(self.expr(a, INT), INT, a) for a in it.args]
            for a, e in zip(it.args, args):
                if not e.type.is_integral and not e.type.is_unknown:
                    raise self.fail(a, "range() needs integers; wrap with int(...)")
            start, stop, step = ("0", args[0].code, "1") if len(args) == 1 else (
                args[0].code, args[1].code, args[2].code if len(args) == 3 else "1")
            neg = False
            if len(args) == 3:
                sv = _const_int(it.args[2])
                if sv is None:
                    raise self.fail(it.args[2], "range() step must be a constant (its sign decides the loop condition)")
                if sv == 0:
                    raise self.fail(it.args[2], "range() step cannot be zero")
                neg = sv < 0
            var = _ident(target)
            cmp = ">" if neg else "<"
            inc = f"{var}++" if step == "1" else (f"{var}--" if step == "-1" else f"{var} += {step}")
            if self.collect:
                self.scope.types[target] = INT
            if loop_scoped:
                self.emit(f"for (int {var} = {start}; {var} {cmp} {stop}; {inc}) {{", s)
                saved = set(self.scope.declared)
                self.scope.declared.add(target)
                self.body(s.body, ret)
                self.scope.declared = saved
            else:
                tmp = self._tmp(target)
                inc_tmp = inc.replace(var, tmp, 1)
                self.emit(f"for (int {tmp} = {start}; {tmp} {cmp} {stop}; {inc_tmp}) {{", s)
                self.out.indent += 1
                self.emit(f"{var} = {tmp};", s)
                self.out.indent -= 1
                self.body(s.body, ret)
            return
        coll = self.expr(it)
        el = self._element_type(coll.type)
        if el is None:
            raise self.fail(it, f"cannot loop over {self._show(coll.type)}")
        el = el.unboxed() if el.unboxed().is_primitive else el
        if self.collect:
            self.scope.types[target] = local_type(el)
        t = self.scope.types.get(target, el)
        if loop_scoped:
            self.emit(f"for ({self.render(t)} {_ident(target)} : {coll.code}) {{", s)
            saved = set(self.scope.declared)
            self.scope.declared.add(target)
            self.body(s.body, ret)
            self.scope.declared = saved
        else:
            tmp = self._tmp(target)
            self.emit(f"for ({self.render(t)} {tmp} : {coll.code}) {{", s)
            self.out.indent += 1
            self.emit(f"{_ident(target)} = {tmp};", s)
            self.out.indent -= 1
            self.body(s.body, ret)

    def enumerate_loop(self, s: ast.For, ret: JType) -> None:
        it = s.iter
        assert isinstance(it, ast.Call)
        if not (isinstance(s.target, ast.Tuple) and len(s.target.elts) == 2
                and all(isinstance(e, ast.Name) for e in s.target.elts)) or len(it.args) != 1:
            raise self.fail(s, "use `for i, x in enumerate(items):`")
        i_name, x_name = (e.id for e in s.target.elts)  # type: ignore[attr-defined]
        if id(s) not in self.plan.loop_scoped:
            raise self.fail(s.target, f"'{i_name}'/'{x_name}' are used after the enumerate loop; "
                                      "copy them to another variable inside the loop")
        coll = self.expr(it.args[0])
        el = self._element_type(coll.type)
        if el is None:
            raise self.fail(it.args[0], f"cannot enumerate {self._show(coll.type)}")
        if self.collect:
            self.scope.types[i_name] = INT
            self.scope.types[x_name] = local_type(el.unboxed() if el.unboxed().is_primitive else el)
        size = f"{_paren(coll, PREC_ATOM)}.length" if coll.type.is_array else f"{_paren(coll, PREC_ATOM)}.size()"
        get = f"{_paren(coll, PREC_ATOM)}[{i_name}]" if coll.type.is_array else f"{_paren(coll, PREC_ATOM)}.get({i_name})"
        xt = self.scope.types.get(x_name, el)
        self.emit(f"for (int {_ident(i_name)} = 0; {_ident(i_name)} < {size}; {_ident(i_name)}++) {{", s)
        saved = set(self.scope.declared)
        self.scope.declared |= {i_name, x_name}
        self.out.indent += 1
        self.emit(f"{self.render(xt)} {_ident(x_name)} = {get};", s)
        self.out.indent -= 1
        self.body(s.body, ret)
        self.scope.declared = saved

    def raise_stmt(self, s: ast.Raise) -> None:
        exc = s.exc
        if exc is None:
            raise self.fail(s, "bare `raise` is not supported")
        name = exc.func.id if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) else (
            exc.id if isinstance(exc, ast.Name) else None)
        if name not in PY_EXCEPTIONS:
            raise self.fail(exc, f"raise one of: {', '.join(PY_EXCEPTIONS)}")
        args = exc.args if isinstance(exc, ast.Call) else []
        msg = self.coerce(self.expr(args[0], STRING), STRING, args[0]).code if args else ""
        self.emit(f"throw new {self.ref(PY_EXCEPTIONS[name])}({msg});", s)

    def try_stmt(self, s: ast.Try, ret: JType) -> None:
        if s.orelse:
            raise self.fail(s, "try/else is not supported")
        if not s.handlers and not s.finalbody:
            raise self.fail(s, "try needs except or finally")
        self.emit("try {", s)
        self.body(s.body, ret, close=False)
        for h in s.handlers:
            self.emit("}", h)
            if h.type is None:
                exc = "java.lang.Exception"
            elif isinstance(h.type, ast.Name) and h.type.id in CATCH_EXCEPTIONS:
                exc = CATCH_EXCEPTIONS[h.type.id]
            else:
                raise self.fail(h, f"catch one of: {', '.join(CATCH_EXCEPTIONS)}")
            var = h.name or "ignored"
            saved = dict(self.scope.types)
            self.scope.types[var] = JType(exc)
            self.scope.declared.add(var)
            if not self.collect:
                self.out.lines[-1] += f" catch ({self.ref(exc)} {_ident(var)}) {{"
            self.body(h.body, ret, close=False)
            self.scope.types = {**saved, **{k: v for k, v in self.scope.types.items() if k != var}}
            self.scope.declared.discard(var)
        if s.finalbody:
            self.emit("}")
            if not self.collect:
                self.out.lines[-1] += " finally {"
            self.body(s.finalbody, ret, close=False)
        self.emit("}")

    def condition(self, node: ast.expr) -> Expr:
        e = self.expr(node, BOOLEAN)
        t = e.type.unboxed()
        if not (t == BOOLEAN or t.is_unknown):
            raise self.fail(node, f"condition is {self._show(e.type)}, not bool; compare explicitly "
                                  "(e.g. `x != 0`, `x is not None`)")
        return e

    def _tmp(self, base: str) -> str:
        self.tmp_counter += 1
        return f"{base}_{self.tmp_counter}" if not self.collect else f"{base}_tmp"

    # ------------------------------------------------------------ expressions

    def literal_type(self, node: ast.expr) -> JType:
        if isinstance(node, ast.Constant):
            v = node.value
            if isinstance(v, bool):
                return BOOLEAN
            if isinstance(v, int):
                return INT if -2**31 <= v < 2**31 else LONG
            if isinstance(v, float):
                return DOUBLE
            if isinstance(v, str):
                return STRING
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return self.literal_type(node.operand)
        return UNKNOWN

    def field_init_type(self, node: ast.expr) -> JType:
        self.scope = Scope({})
        self.collect = True
        return self.expr(node).type

    def expr(self, node: ast.expr, expected: JType | None = None) -> Expr:
        method = getattr(self, "e_" + type(node).__name__, None)
        if method is None:
            raise self.fail(node, _unsupported_expr_message(node))
        return method(node, expected)

    def e_Constant(self, node: ast.Constant, expected: JType | None) -> Expr:
        v = node.value
        if v is None:
            return Expr("null", NULL)
        if isinstance(v, bool):
            return Expr("true" if v else "false", BOOLEAN)
        if isinstance(v, int):
            if expected is not None and expected.unboxed().name in ("double", "float") :
                return Expr(f"{v}.0" if expected.unboxed().name == "double" else f"{v}f", expected.unboxed())
            if -2**31 <= v < 2**31:
                return Expr(str(v), INT)
            return Expr(f"{v}L", LONG)
        if isinstance(v, float):
            if v != v:
                return Expr("Double.NaN", DOUBLE)
            if v in (float("inf"), float("-inf")):
                return Expr("Double.POSITIVE_INFINITY" if v > 0 else "Double.NEGATIVE_INFINITY", DOUBLE)
            text = repr(v)
            if "e" not in text and "." not in text:
                text += ".0"
            return Expr(text, DOUBLE)
        if isinstance(v, str):
            return Expr(_literal(v), STRING)
        raise self.fail(node, f"unsupported literal {v!r}")

    def e_JoinedStr(self, node: ast.JoinedStr, expected: JType | None) -> Expr:
        parts: list[str] = []
        fmt: list[str] = []
        args: list[str] = []
        needs_format = any(isinstance(v, ast.FormattedValue) and (v.format_spec or v.conversion not in (-1, None))
                           for v in node.values)
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(_literal(v.value))
                fmt.append(str(v.value).replace("%", "%%"))
            elif isinstance(v, ast.FormattedValue):
                e = self.expr(v.value)
                spec = ""
                if v.format_spec is not None:
                    if not (isinstance(v.format_spec, ast.JoinedStr) and all(isinstance(x, ast.Constant) for x in v.format_spec.values)):
                        raise self.fail(v, "format spec must be a literal, e.g. {x:.2f}")
                    spec = "".join(str(x.value) for x in v.format_spec.values)  # type: ignore[attr-defined]
                fmt.append(_java_format(spec, e.type, v))
                args.append(e.code)
                parts.append(_paren(e, PREC_ADD + 1))
        if needs_format:
            code = f"String.format({_literal(''.join(fmt))}{''.join(', ' + a for a in args)})"
            return Expr(code, STRING)
        if not parts:
            return Expr('""', STRING)
        if not isinstance(node.values[0], ast.Constant):
            parts.insert(0, '""')
        return Expr(" + ".join(parts), STRING, PREC_ADD)

    def e_Name(self, node: ast.Name, expected: JType | None) -> Expr:
        name = node.id
        sc = self.scope
        if sc is not None and name in sc.params:
            return Expr(_ident(name), sc.params[name])
        if sc is not None and name in sc.types:
            return Expr(_ident(name), sc.types[name])
        if sc is not None and self.method is not None and self._is_local(name):
            if self.collect:
                return Expr(_ident(name), UNKNOWN)
            raise self.fail(node, f"'{name}' is used before it is assigned")
        if name == "self":
            if self.static_ctx:
                raise self.fail(node, "`self` is not available in a @staticmethod")
            return Expr("this", JType(self.c.fqn))
        bound = self.f.names.get(name)
        if isinstance(bound, ClassRef):
            return Expr(self.ref(bound.fqn), UNKNOWN, cls=bound)
        if name in ("True", "False", "None"):
            return self.e_Constant(ast.Constant({"True": True, "False": False, "None": None}[name]), expected)
        if isinstance(bound, tuple) and bound[0] == "mathattr":
            return self.math_attr(node, bound[1])
        if name in PY_EXCEPTIONS or name in CATCH_EXCEPTIONS:
            raise self.fail(node, f"'{name}' can only be used in raise/except")
        raise self.fail(node, f"undefined name '{name}'" + (" (fields need `self.`)" if name in self.c.fields else ""))

    def _is_local(self, name: str) -> bool:
        if self.method is None:
            return False
        for sub in _walk_function(self.method):
            if isinstance(sub, ast.Name) and sub.id == name and isinstance(sub.ctx, ast.Store):
                return True
        return False

    def math_attr(self, node: ast.AST, attr: str) -> Expr:
        if attr in MATH_CONSTS:
            c = MATH_CONSTS[attr]
            return Expr(c if "." in c or "(" in c else f"Math.{c}", DOUBLE)
        raise self.fail(node, f"math.{attr} is not a constant; call it")

    def e_Attribute(self, node: ast.Attribute, expected: JType | None) -> Expr:
        if isinstance(node.value, ast.Name) and self.f.names.get(node.value.id) == "math":
            return self.math_attr(node, node.attr)
        obj = self.expr(node.value)
        attr = node.attr
        if obj.cls is not None:
            nested = self.db.nested(obj.cls.fqn, attr)
            if nested is not None:
                return Expr(self.ref(nested), UNKNOWN, cls=ClassRef(nested))
            cdata = self.db.get(obj.cls.fqn) or {}
            if attr in cdata.get("enumConstants", []):
                return Expr(f"{obj.code}.{attr}", JType(obj.cls.fqn))
            f = self.db.field(JType(obj.cls.fqn), attr)
            if f is not None:
                return Expr(f"{obj.code}.{_ident(attr)}", f.return_type())
            if obj.cls.fqn in self.db.classes:
                raise self.fail(node, f"{obj.cls.fqn.rsplit('.', 1)[-1]} has no static field, enum constant or nested class '{attr}'")
            return Expr(f"{obj.code}.{attr}", UNKNOWN)
        if obj.type.is_array and attr == "length":
            return Expr(f"{_paren(obj, PREC_ATOM)}.length", INT)
        f = self.db.field(obj.type, attr) if not obj.type.is_unknown else None
        if f is not None:
            if obj.code == "this":
                shadowed = self.scope is not None and (attr in self.scope.params or attr in self.scope.types)
                return Expr(f"this.{_ident(attr)}" if shadowed else _ident(attr), f.return_type())
            return Expr(f"{_paren(obj, PREC_ATOM)}.{_ident(attr)}", f.return_type())
        if obj.code == "this":
            if self.db.methods(obj.type, attr):
                raise self.fail(node, f"'{attr}' is a method; call it with ()")
            raise self.fail(node, f"{self.c.node.name} has no field '{attr}'; declare it in the class body "
                                  f"(e.g. `{attr}: DcMotor`)")
        if self._known_complete(obj.type) and not self.db.methods(obj.type, attr):
            raise self.fail(node, f"{self._show(obj.type)} has no field '{attr}'")
        return Expr(f"{_paren(obj, PREC_ATOM)}.{attr}", UNKNOWN)

    def e_Call(self, node: ast.Call, expected: JType | None) -> Expr:
        fn = node.func
        if isinstance(fn, ast.Name):
            builtin = getattr(self, "b_" + fn.id, None)
            bound = self.f.names.get(fn.id)
            if isinstance(bound, tuple) and bound[0] == "mathattr":
                return self.math_call(node, bound[1])
            if isinstance(bound, ClassRef):
                return self.construct(node, bound.fqn, expected)
            if builtin is not None and not (self.scope and (fn.id in self.scope.types or fn.id in self.scope.params)):
                return builtin(node, expected)
            if fn.id in PY_EXCEPTIONS:
                raise self.fail(node, "exceptions can only be raised")
            raise self.fail(node, f"'{fn.id}' is not callable here (methods need `self.`, functions need a class)")
        if isinstance(fn, ast.Attribute):
            if isinstance(fn.value, ast.Name) and self.f.names.get(fn.value.id) == "math":
                return self.math_call(node, fn.attr)
            if (isinstance(fn.value, ast.Call) and isinstance(fn.value.func, ast.Name) and fn.value.func.id == "super"):
                return self.super_call(node, fn.attr)
            obj = self.expr(fn.value)
            if obj.cls is not None:
                nested = self.db.nested(obj.cls.fqn, fn.attr)
                if nested is not None:  # IMU.Parameters(...) creates the nested class
                    return self.construct(node, nested, expected)
                return self.method_call(node, obj, JType(obj.cls.fqn), fn.attr, static=True)
            return self.method_call(node, obj, obj.type, fn.attr, static=False)
        raise self.fail(node, "unsupported call")

    def super_call(self, node: ast.Call, attr: str) -> Expr:
        if self.c.superclass is None:
            raise self.fail(node, "super() needs a base class")
        if attr == "__init__":
            ctors = self.db.constructors(self.c.superclass.name)
            args = self.call_args(node, ctors, "super") if ctors else [self.expr(a).code for a in node.args]
            return Expr(f"super({', '.join(args)})", VOID)
        members = self.db.methods(self.c.superclass, attr)
        if not members:
            raise self.fail(node, f"{self.c.superclass.simple} has no method '{attr}'")
        member, args, ret = self.resolve_call(node, members, attr)
        return Expr(f"super.{attr}({', '.join(args)})", ret)

    def construct(self, node: ast.Call, fqn: str, expected: JType | None) -> Expr:
        data = self.db.get(fqn) or {}
        if data.get("kind") in ("interface", "enum", "annotation"):
            raise self.fail(node, f"cannot create a {fqn.rsplit('.', 1)[-1]} ({data['kind']}); "
                                  "hardware comes from self.hardwareMap.get(Type, \"name\")")
        if data.get("abstract"):
            raise self.fail(node, f"{fqn.rsplit('.', 1)[-1]} is abstract and cannot be created directly")
        ctors = self.db.constructors(fqn)
        args = self.call_args(node, ctors, fqn.rsplit(".", 1)[-1]) if ctors else [self.expr(a).code for a in node.args]
        diamond = "<>" if data.get("typeParams") else ""
        t = JType(fqn, expected.args if expected is not None and expected.name == fqn else ())
        return Expr(f"new {self.ref(fqn)}{diamond}({', '.join(args)})", t)

    def call_args(self, node: ast.Call, members: list[Member], what: str) -> list[str]:
        _, args, _ = self.resolve_call(node, members, what)
        return args

    def method_call(self, node: ast.Call, obj: Expr, recv: JType, name: str, static: bool) -> Expr:
        # Python spellings on builtin containers
        if self._is(recv, "java.util.List"):
            if name == "pop":
                if node.args:
                    idx = self.index_expr(obj, node.args[0])
                    return Expr(f"{_paren(obj, PREC_ATOM)}.remove({idx})", self._type_arg(recv, "java.util.List", 0))
                return Expr(f"{_paren(obj, PREC_ATOM)}.remove({_paren(obj, PREC_ATOM)}.size() - 1)",
                            self._type_arg(recv, "java.util.List", 0))
            if name == "remove" and node.args:
                el = self._type_arg(recv, "java.util.List", 0)
                a = self.expr(node.args[0], el)
                # List.remove(int) would remove by index; Python's remove is by value
                cast = "(Object) " if a.type.unboxed().is_integral else ""
                return Expr(f"{_paren(obj, PREC_ATOM)}.remove({cast}{a.code})", BOOLEAN)
            name = LIST_METHODS.get(name, name)
        elif recv.is_string:
            if name == "split" and not node.args:
                return Expr(f'{_paren(obj, PREC_ATOM)}.trim().split("\\\\s+")', JType("java.lang.String", (), 1))
            if name == "join" and len(node.args) == 1:
                seq = self.expr(node.args[0])
                return Expr(f"String.join({obj.code}, {seq.code})", STRING)
            name = STR_METHODS.get(name, name)
        elif self._is(recv, "java.util.Map"):
            if name == "items":
                raise self.fail(node, "dict.items() is not supported; loop over d.keySet() and use d[key]")
            name = {"keys": "keySet"}.get(name, name)

        if recv.is_unknown:
            args = [self.expr(a).code for a in node.args]
            if node.keywords:
                raise self.fail(node, "keyword arguments need a known receiver type")
            return Expr(f"{_paren(obj, PREC_ATOM)}.{name}({', '.join(args)})", UNKNOWN)
        members = self.db.methods(recv, name)
        if static:
            members = [m for m in members if m.data.get("static")] or members
        if not members:
            if self._known_complete(recv):
                what = self._show(recv)
                hint = ""
                if self.db.field(recv, name) is not None:
                    hint = f" ('{name}' is a field; drop the parentheses)"
                raise self.fail(node.func, f"{what} has no method '{name}'{hint}")
            args = [self.expr(a).code for a in node.args]
            return Expr(f"{_paren(obj, PREC_ATOM)}.{name}({', '.join(args)})", UNKNOWN)
        member, args, ret = self.resolve_call(node, members, name)
        if obj.code == "this":
            if self.static_ctx:
                raise self.fail(node, "`self` is not available in a @staticmethod")
            return Expr(f"{_ident(name)}({', '.join(args)})", ret)
        return Expr(f"{_paren(obj, PREC_ATOM)}.{name}({', '.join(args)})", ret)

    def resolve_call(self, node: ast.Call, members: list[Member], what: str) -> tuple[Member, list[str], JType]:
        """Pick the overload and render arguments. Keyword arguments are
        matched to the Java parameter names from the SDK sources."""
        n_args = len(node.args) + len(node.keywords)
        if any(isinstance(a, ast.Starred) for a in node.args):
            raise self.fail(node, "*args in calls are not supported")
        cands = [m for m in members if len(m.data["params"]) == n_args
                 or (m.varargs and n_args >= len(m.data["params"]) - 1)]
        if not cands:
            arities = sorted({len(m.data["params"]) for m in members})
            sigs = "; ".join(self._sig(m) for m in members[:4])
            raise self.fail(node, f"{what}() takes {' or '.join(map(str, arities))} argument(s), got {n_args}: {sigs}")

        best: tuple[int, Member, list[ast.expr]] | None = None
        for m in cands:
            ordered = self._order_args(node, m)
            if ordered is None:
                continue
            ptypes = m.param_types()
            score, ok = 0, True
            for i, a in enumerate(ordered):
                pt = ptypes[min(i, len(ptypes) - 1)]
                if m.varargs and i >= len(ptypes) - 1 and not (len(ordered) == len(ptypes) and self._probe(a).type.is_array):
                    pt = pt.element()
                s = self._compat(self._probe(a), pt)
                if s < 0:
                    ok = False
                    break
                score += s
            if ok and (best is None or score > best[0]):
                best = (score, m, ordered)
        if best is None:
            m = cands[0]
            ordered = self._order_args(node, m)
            if ordered is None:
                raise self.fail(node, f"no parameter matches those keyword arguments: {self._sig(m)}")
            for i, (a, pt) in enumerate(zip(ordered, m.param_types())):
                e = self._probe(a)
                if self._compat(e, pt) < 0:
                    raise self.fail(a, f"argument {i + 1} of {what}() is {self._show(e.type)}, expected "
                                       f"{self._show(pt)}{self._numeric_hint(e.type, pt)}: {self._sig(m)}")
            raise self.fail(node, f"no matching overload for {what}(): {self._sig(m)}")

        _, m, ordered = best
        ptypes = m.param_types()
        method_env: dict[str, JType] = {}
        tparams = [type_var_name(tp) for tp in m.data.get("typeParams", [])]
        rendered = []
        for i, a in enumerate(ordered):
            pt = ptypes[min(i, len(ptypes) - 1)]
            if m.varargs and i >= len(ptypes) - 1:
                pt = pt.element() if not (len(ordered) == len(ptypes) and self._probe(a).type.is_array) else pt
            e = self.expr(a, pt)
            if e.cls is not None and pt.name == "java.lang.Class":
                if pt.args and pt.args[0].name in tparams:
                    method_env[pt.args[0].name] = JType(e.cls.fqn)
                rendered.append(f"{e.code}.class")
                continue
            if pt.name in tparams and not pt.args and not e.type.is_unknown:
                method_env.setdefault(pt.name, e.type.boxed())
            rendered.append(self.coerce(e, pt, a).code)
        ret = substitute(m.return_type(), method_env)
        if ret.name in tparams:
            ret = UNKNOWN
        return m, rendered, ret

    def _order_args(self, node: ast.Call, m: Member) -> list[ast.expr] | None:
        if not node.keywords:
            return list(node.args)
        names = [p["name"] for p in m.data["params"]]
        slots: list[ast.expr | None] = list(node.args) + [None] * (len(names) - len(node.args))
        for kw in node.keywords:
            if kw.arg is None or kw.arg not in names:
                return None
            i = names.index(kw.arg)
            if i < len(node.args) or slots[i] is not None:
                return None
            slots[i] = kw.value
        if any(s is None for s in slots):
            return None
        return slots  # type: ignore[return-value]

    def _probe(self, node: ast.expr) -> Expr:
        saved = self.collect
        self.collect = True
        try:
            return self.expr(node)
        except Unsupported:
            return Expr("?", UNKNOWN)
        finally:
            self.collect = saved

    def _compat(self, e: Expr, pt: JType) -> int:
        """-1 incompatible, higher is a better match."""
        t = e.type
        if e.cls is not None:
            return 3 if pt.name == "java.lang.Class" else -1
        if t.is_unknown or pt.is_unknown or (len(pt.name) <= 2 and pt.name[:1].isupper()):
            return 1
        if t == NULL:
            return -1 if pt.is_primitive else 1
        if t == pt:
            return 4
        tu, pu = t.unboxed(), pt.unboxed()
        if tu.is_primitive or pu.is_primitive:
            if tu == pu:
                return 3
            if pt.name == "java.lang.Object" and not pt.dims:
                return 1  # boxing: addData("pressed", touch.isPressed())
            if tu.name == "boolean" or pu.name == "boolean":
                return -1
            if tu.is_numeric and pu.is_numeric:
                from .jtypes import NUMERIC_RANK
                if NUMERIC_RANK[tu.name] <= NUMERIC_RANK[pu.name]:
                    return 2
                if pu.name == "float" and tu.name == "double":
                    return 1  # coerce() casts; Python has no float32
                if isinstance(e.code, str) and e.code.lstrip("-").isdigit() and pu.name in ("byte", "short", "char"):
                    return 1
                return -1
            if pt.name == "java.lang.Object":
                return 1
            return -1
        if pt.name == "java.lang.Object":
            return 1
        sub = self.db.is_subtype(t.erasure(), pt.erasure())
        if sub is None:
            return 1
        if pt.name in ("java.lang.CharSequence",) and t.is_string:
            return 2
        return 2 if sub else -1

    def coerce(self, e: Expr, target: JType, node: ast.AST) -> Expr:
        if target is None or target.is_unknown or e.type.is_unknown or e.cls is not None:
            return e
        tu, eu = target.unboxed(), e.type.unboxed()
        if tu.name == "float" and eu.name == "double" and not target.dims:
            return Expr(f"(float) {_paren(e, PREC_UNARY)}", JType("float"), PREC_UNARY)
        if tu.is_numeric and eu.is_numeric and tu.is_integral and not eu.is_integral:
            raise self.fail(node, f"{self._show(e.type)} value where {self._show(target)} is needed; "
                                  "convert explicitly with int(...) or round(...)")
        if target.name in ("java.lang.Double", "java.lang.Float") and eu.is_integral:
            return Expr(f"(double) {_paren(e, PREC_UNARY)}", DOUBLE, PREC_UNARY)
        return e

    def _numeric_hint(self, t: JType, pt: JType) -> str:
        if pt.unboxed().is_integral and t.unboxed().is_numeric and not t.unboxed().is_integral:
            return " (convert with int(...))"
        return ""

    def _sig(self, m: Member) -> str:
        ps = ", ".join(f"{p['name']}: {self._show(t)}" for p, t in zip(m.data["params"], m.param_types()))
        ret = m.return_type()
        return f"{m.data['name']}({ps})" + ("" if ret == VOID else f" -> {self._show(ret)}")

    def _show(self, t: JType) -> str:
        """Python-flavoured type name for messages."""
        u = t.unboxed()
        py = {"double": "float", "float": "float", "int": "int", "long": "int", "short": "int", "byte": "int",
              "boolean": "bool", "java.lang.String": "str", "void": "None", "null": "None", "?": "unknown"}
        if t.dims:
            return f"{self._show(JType(t.name, t.args))}[]"
        if u.name in py:
            return py[u.name]
        if t.name == "java.util.List" and t.args:
            return f"list[{self._show(t.args[0])}]"
        if t.name == "java.util.Map" and len(t.args) == 2:
            return f"dict[{self._show(t.args[0])}, {self._show(t.args[1])}]"
        return t.simple

    def _known_complete(self, t: JType) -> bool:
        """True when the DB knows the type and all its supertypes, so a missing
        member is a real error rather than a gap in our JDK slice."""
        if t.is_unknown or t.is_primitive or t.dims or t.name not in self.db.classes:
            return False
        for sup in self.db.supertypes(t):
            if sup.name not in self.db.classes:
                return False
        return not t.name.startswith("java.")

    def _is(self, t: JType, fqn: str) -> bool:
        if t.dims:
            return False
        return t.name == fqn or any(s.name == fqn for s in self.db.supertypes(t))

    def _type_arg(self, t: JType, fqn: str, i: int) -> JType:
        for cand in [t, *self.db.supertypes(t)]:
            if cand.name == fqn:
                return cand.args[i] if len(cand.args) > i else UNKNOWN
        return UNKNOWN

    def _element_type(self, t: JType) -> JType | None:
        if t.is_array:
            return t.element()
        if t.is_unknown:
            return UNKNOWN
        for cand in [t, *self.db.supertypes(t)]:
            if cand.name in ("java.lang.Iterable", "java.util.Collection", "java.util.List", "java.util.Set"):
                return cand.args[0] if cand.args else OBJECT
        return None

    def index_expr(self, obj: Expr, idx_node: ast.expr) -> str:
        c = _const_int(idx_node)
        if c is not None and c < 0:
            size = f"{_paren(obj, PREC_ATOM)}.length" if obj.type.is_array else f"{_paren(obj, PREC_ATOM)}.size()"
            return f"{size} - {-c}"
        idx = self.expr(idx_node, INT)
        if not idx.type.unboxed().is_integral and not idx.type.is_unknown:
            raise self.fail(idx_node, "index must be an int")
        return idx.code

    def e_Subscript(self, node: ast.Subscript, expected: JType | None) -> Expr:
        if isinstance(node.slice, ast.Slice):
            raise self.fail(node, "slices are not supported")
        obj = self.expr(node.value)
        if obj.type.is_array:
            return Expr(f"{_paren(obj, PREC_ATOM)}[{self.index_expr(obj, node.slice)}]", obj.type.element())
        if self._is(obj.type, "java.util.List"):
            el = self._type_arg(obj.type, "java.util.List", 0)
            return Expr(f"{_paren(obj, PREC_ATOM)}.get({self.index_expr(obj, node.slice)})", el)
        if self._is(obj.type, "java.util.Map"):
            k = self.expr(node.slice, self._type_arg(obj.type, "java.util.Map", 0))
            return Expr(f"{_paren(obj, PREC_ATOM)}.get({k.code})", self._type_arg(obj.type, "java.util.Map", 1))
        if obj.type.is_string:
            return Expr(f"String.valueOf({_paren(obj, PREC_ATOM)}.charAt({self.index_expr(obj, node.slice)}))", STRING)
        if obj.type.is_unknown:
            raise self.fail(node, "cannot index a value of unknown type; annotate the variable")
        raise self.fail(node, f"{self._show(obj.type)} cannot be indexed")

    def e_List(self, node: ast.List, expected: JType | None) -> Expr:
        el = expected.args[0] if expected is not None and expected.name == "java.util.List" and expected.args else None
        items = [self.expr(e, el) for e in node.elts]
        if el is None:
            if not items:
                raise self.fail(node, "empty list needs a type: `xs: list[float] = []`")
            el = items[0].type
            for it in items[1:]:
                el = _widen(el, it.type)
        el = local_type(el.unboxed()).boxed() if el.unboxed().is_primitive else el
        lt = JType("java.util.List", (el,))
        arraylist = self.ref("java.util.ArrayList")
        if not items:
            return Expr(f"new {arraylist}<>()", lt)
        codes = [self.coerce(i, el, n).code for i, n in zip(items, node.elts)]
        return Expr(f"new {arraylist}<>({self.ref('java.util.Arrays')}.asList({', '.join(codes)}))", lt)

    def e_Dict(self, node: ast.Dict, expected: JType | None) -> Expr:
        if node.keys:
            raise self.fail(node, "dict literals must be empty; fill with d[key] = value")
        if expected is None or expected.name != "java.util.Map":
            raise self.fail(node, "empty dict needs a type: `d: dict[str, float] = {}`")
        return Expr(f"new {self.ref('java.util.HashMap')}<>()", expected)

    def e_IfExp(self, node: ast.IfExp, expected: JType | None) -> Expr:
        cond = self.condition(node.test)
        a, b = self.expr(node.body, expected), self.expr(node.orelse, expected)
        t = a.type if a.type == b.type else (numeric_promote(a.type, b.type) if a.type.is_numeric and b.type.is_numeric
                                             else (b.type if a.type == NULL else a.type))
        return Expr(f"{_paren(cond, PREC_OR)} ? {_paren(a, PREC_OR)} : {_paren(b, PREC_TERNARY)}", t, PREC_TERNARY)

    def e_UnaryOp(self, node: ast.UnaryOp, expected: JType | None) -> Expr:
        e = self.expr(node.operand, expected)
        if isinstance(node.op, ast.Not):
            if e.type.unboxed() != BOOLEAN and not e.type.is_unknown:
                raise self.fail(node, f"`not` needs a bool, got {self._show(e.type)}")
            return Expr(f"!{_paren(e, PREC_UNARY)}", BOOLEAN, PREC_UNARY)
        op = {ast.USub: "-", ast.UAdd: "+", ast.Invert: "~"}[type(node.op)]
        t = e.type.unboxed() if e.type.unboxed().is_numeric else e.type
        if t.is_numeric and t.name in ("byte", "short", "char"):
            t = INT
        inner = _paren(e, PREC_UNARY)
        if op == "-" and inner.startswith("-"):
            inner = f"({inner})"
        return Expr(f"{op}{inner}", t, PREC_UNARY)

    def e_BoolOp(self, node: ast.BoolOp, expected: JType | None) -> Expr:
        op, prec = ("&&", PREC_AND) if isinstance(node.op, ast.And) else ("||", PREC_OR)
        parts = []
        for v in node.values:
            e = self.expr(v, BOOLEAN)
            if e.type.unboxed() != BOOLEAN and not e.type.is_unknown:
                raise self.fail(v, f"`{'and' if op == '&&' else 'or'}` operands must be bool, got {self._show(e.type)} "
                                   "(Java has no truthiness)")
            parts.append(_paren(e, prec + 1))
        return Expr(f" {op} ".join(parts), BOOLEAN, prec)

    def e_Compare(self, node: ast.Compare, expected: JType | None) -> Expr:
        pieces = []
        left_node = node.left
        left = self.expr(left_node)
        for op, right_node in zip(node.ops, node.comparators):
            right = self.expr(right_node, left.type if left.type.is_numeric else None)
            pieces.append(self.compare_one(node, left, op, right))
            left_node, left = right_node, right
        if len(pieces) == 1:
            return pieces[0]
        return Expr(" && ".join(_paren(p, PREC_AND + 1) for p in pieces), BOOLEAN, PREC_AND)

    def compare_one(self, node: ast.AST, a: Expr, op: ast.cmpop, b: Expr) -> Expr:
        if isinstance(op, (ast.Is, ast.IsNot)):
            j = "==" if isinstance(op, ast.Is) else "!="
            return Expr(f"{_paren(a, PREC_EQ)} {j} {_paren(b, PREC_REL)}", BOOLEAN, PREC_EQ)
        if isinstance(op, (ast.In, ast.NotIn)):
            neg = "!" if isinstance(op, ast.NotIn) else ""
            if self._is(b.type, "java.util.Map"):
                code = f"{_paren(b, PREC_ATOM)}.containsKey({a.code})"
            elif self._is(b.type, "java.util.Collection") or b.type.is_string:
                code = f"{_paren(b, PREC_ATOM)}.contains({a.code})"
            else:
                raise self.fail(node, f"`in` is not supported on {self._show(b.type)}")
            return Expr(f"{neg}{code}", BOOLEAN, PREC_UNARY if neg else PREC_ATOM)
        j = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}[type(op)]
        if j in ("==", "!=") and (a.type.is_string or b.type.is_string) and a.type != NULL and b.type != NULL:
            code = f"{_paren(a, PREC_ATOM)}.equals({b.code})"
            return Expr(("!" + code) if j == "!=" else code, BOOLEAN, PREC_UNARY if j == "!=" else PREC_ATOM)
        if j in ("==", "!=") and (a.type == NULL or b.type == NULL):
            self.warn(node, "use `is None` / `is not None` to compare with None")
        if j in ("<", "<=", ">", ">=") and not (a.type.is_numeric or a.type.is_unknown) :
            raise self.fail(node, f"cannot order-compare {self._show(a.type)}")
        prec = PREC_EQ if j in ("==", "!=") else PREC_REL
        return Expr(f"{_paren(a, prec)} {j} {_paren(b, prec + 1)}", BOOLEAN, prec)

    def _binop_type(self, a: JType, op: ast.operator, b: JType) -> JType:
        if a.is_unknown or b.is_unknown:
            return UNKNOWN
        if isinstance(op, ast.Add) and (a.is_string or b.is_string):
            return STRING
        if isinstance(op, ast.Div) or isinstance(op, ast.Pow):
            return DOUBLE if not (isinstance(op, ast.Div) and False) else DOUBLE
        if a.is_numeric and b.is_numeric:
            return numeric_promote(a, b)
        return UNKNOWN

    def e_BinOp(self, node: ast.BinOp, expected: JType | None) -> Expr:
        return self.binop(node, expected)

    def binop(self, node: ast.BinOp, expected: JType | None = None) -> Expr:
        a = self.expr(node.left, expected if expected is not None and expected.is_numeric else None)
        b = self.expr(node.right, expected if expected is not None and expected.is_numeric else None)
        op = node.op
        if isinstance(op, ast.Add) and (a.type.is_string or b.type.is_string):
            if not (a.type.is_string and (b.type.is_string or b.type.is_unknown)) and not (
                    b.type.is_string and a.type.is_unknown):
                raise self.fail(node, "can't add str and non-str; use an f-string: f\"x={x}\"")
            return Expr(f"{_paren(a, PREC_ADD)} + {_paren(b, PREC_ADD + 1)}", STRING, PREC_ADD)
        if isinstance(op, ast.Mod) and a.type.is_string:
            raise self.fail(node, "%-formatting is not supported; use an f-string")
        for side, e in (("left", a), ("right", b)):
            if not (e.type.is_numeric or e.type.is_unknown):
                raise self.fail(node, f"arithmetic on {self._show(e.type)} is not supported")
        t = numeric_promote(a.type, b.type) if not (a.type.is_unknown or b.type.is_unknown) else UNKNOWN
        both_int = a.type.is_integral and b.type.is_integral
        if isinstance(op, ast.Div):
            if both_int:
                return Expr(f"(double) {_paren(a, PREC_UNARY)} / {_paren(b, PREC_MUL + 1)}", DOUBLE, PREC_MUL)
            return Expr(f"{_paren(a, PREC_MUL)} / {_paren(b, PREC_MUL + 1)}", DOUBLE if not t.is_unknown else t, PREC_MUL)
        if isinstance(op, ast.FloorDiv):
            if both_int:
                return Expr(f"Math.floorDiv({a.code}, {b.code})", t)
            return Expr(f"Math.floor({_paren(a, PREC_MUL)} / {_paren(b, PREC_MUL + 1)})", DOUBLE)
        if isinstance(op, ast.Mod):
            if both_int:
                return Expr(f"Math.floorMod({a.code}, {b.code})", t)
            # Python's % takes the sign of the divisor; Java's takes the dividend.
            return Expr(f"(({_paren(a, PREC_MUL)} % {_paren(b, PREC_MUL + 1)}) + {_paren(b, PREC_ADD + 1)}) % "
                        f"{_paren(b, PREC_MUL + 1)}", DOUBLE if not t.is_unknown else t, PREC_MUL)
        if isinstance(op, ast.Pow):
            return Expr(f"Math.pow({a.code}, {b.code})", DOUBLE)
        j, prec = {ast.Add: ("+", PREC_ADD), ast.Sub: ("-", PREC_ADD), ast.Mult: ("*", PREC_MUL),
                   ast.BitAnd: ("&", PREC_BITAND), ast.BitOr: ("|", PREC_BITOR), ast.BitXor: ("^", PREC_BITXOR),
                   ast.LShift: ("<<", PREC_SHIFT), ast.RShift: (">>", PREC_SHIFT)}.get(type(op), (None, 0))
        if j is None:
            raise self.fail(node, f"operator {type(op).__name__} is not supported")
        if j in ("&", "|", "^", "<<", ">>") and not (both_int or a.type.is_unknown or b.type.is_unknown):
            raise self.fail(node, "bitwise operators need ints")
        return Expr(f"{_paren(a, prec)} {j} {_paren(b, prec + 1)}", t, prec)

    def e_Lambda(self, node: ast.Lambda, expected: JType | None) -> Expr:
        names = [a.arg for a in node.args.args]
        saved = self.scope
        self.scope = Scope(dict(saved.params) if saved else {}, types=dict(saved.types) if saved else {})
        for n in names:
            self.scope.params[n] = UNKNOWN
        body = self.expr(node.body)
        self.scope = saved
        params = names[0] if len(names) == 1 else f"({', '.join(names)})"
        return Expr(f"{params} -> {body.code}", UNKNOWN, PREC_TERNARY)

    # ------------------------------------------------------------ builtins

    def _one_arg(self, node: ast.Call, name: str) -> ast.expr:
        if len(node.args) != 1 or node.keywords:
            raise self.fail(node, f"{name}() takes exactly one argument here")
        return node.args[0]

    def b_print(self, node: ast.Call, expected: JType | None) -> Expr:
        parts = [self.expr(a) for a in node.args]
        text = " + \" \" + ".join(_paren(p, PREC_ADD + 1) for p in parts) if parts else '""'
        if parts and not parts[0].type.is_string:
            text = '"" + ' + text
        self.warn(node, "print() goes to the robot log (logcat), not the Driver Hub; use self.telemetry to see values")
        return Expr(f"System.out.println({text})", VOID)

    def b_len(self, node: ast.Call, expected: JType | None) -> Expr:
        e = self.expr(self._one_arg(node, "len"))
        if e.type.is_array:
            return Expr(f"{_paren(e, PREC_ATOM)}.length", INT)
        if e.type.is_string:
            return Expr(f"{_paren(e, PREC_ATOM)}.length()", INT)
        if self._is(e.type, "java.util.Collection") or self._is(e.type, "java.util.Map"):
            return Expr(f"{_paren(e, PREC_ATOM)}.size()", INT)
        raise self.fail(node, f"len() of {self._show(e.type)} is not supported")

    def b_abs(self, node: ast.Call, expected: JType | None) -> Expr:
        e = self.expr(self._one_arg(node, "abs"))
        return Expr(f"Math.abs({e.code})", local_type(e.type.unboxed()) if e.type.is_numeric else UNKNOWN)

    def _minmax(self, node: ast.Call, name: str) -> Expr:
        if len(node.args) < 2 or node.keywords:
            raise self.fail(node, f"{name}() needs two or more numbers (lists are not supported)")
        es = [self.expr(a) for a in node.args]
        acc = es[0]
        for e in es[1:]:
            t = numeric_promote(acc.type, e.type) if acc.type.is_numeric and e.type.is_numeric else UNKNOWN
            acc = Expr(f"Math.{name}({acc.code}, {e.code})", t)
        return acc

    def b_min(self, node: ast.Call, expected: JType | None) -> Expr:
        return self._minmax(node, "min")

    def b_max(self, node: ast.Call, expected: JType | None) -> Expr:
        return self._minmax(node, "max")

    def b_round(self, node: ast.Call, expected: JType | None) -> Expr:
        if len(node.args) == 2:
            raise self.fail(node, "round(x, ndigits) is not supported; format with f\"{x:.2f}\" for display")
        e = self.expr(self._one_arg(node, "round"))
        # Java rounds .5 up, Python rounds half to even; acceptable for robot values
        return Expr(f"(int) Math.round({e.code})", INT, PREC_UNARY)

    def b_int(self, node: ast.Call, expected: JType | None) -> Expr:
        e = self.expr(self._one_arg(node, "int"))
        if e.type.is_string:
            return Expr(f"Integer.parseInt({e.code})", INT)
        if e.type.unboxed().is_integral:
            return e
        return Expr(f"(int) {_paren(e, PREC_UNARY)}", INT, PREC_UNARY)

    def b_float(self, node: ast.Call, expected: JType | None) -> Expr:
        e = self.expr(self._one_arg(node, "float"))
        if e.type.is_string:
            return Expr(f"Double.parseDouble({e.code})", DOUBLE)
        return Expr(f"(double) {_paren(e, PREC_UNARY)}", DOUBLE, PREC_UNARY)

    def b_str(self, node: ast.Call, expected: JType | None) -> Expr:
        e = self.expr(self._one_arg(node, "str"))
        return Expr(f"String.valueOf({e.code})", STRING)

    def b_bool(self, node: ast.Call, expected: JType | None) -> Expr:
        raise self.fail(node, "bool() is not supported; compare explicitly (x != 0)")

    def b_isinstance(self, node: ast.Call, expected: JType | None) -> Expr:
        if len(node.args) != 2:
            raise self.fail(node, "isinstance(obj, Class)")
        obj, cls = self.expr(node.args[0]), self.expr(node.args[1])
        if cls.cls is None:
            raise self.fail(node.args[1], "second argument must be a class")
        return Expr(f"{_paren(obj, PREC_REL)} instanceof {cls.code}", BOOLEAN, PREC_REL)

    def b_range(self, node: ast.Call, expected: JType | None) -> Expr:
        raise self.fail(node, "range() can only be used directly in a for loop")

    def b_list(self, node: ast.Call, expected: JType | None) -> Expr:
        if node.args:
            raise self.fail(node, "list(x) is not supported; use [] with a type annotation")
        return self.e_List(ast.copy_location(ast.List([], ast.Load()), node), expected)

    def b_dict(self, node: ast.Call, expected: JType | None) -> Expr:
        if node.args:
            raise self.fail(node, "dict(x) is not supported")
        return self.e_Dict(ast.copy_location(ast.Dict([], []), node), expected)

    def math_call(self, node: ast.Call, name: str) -> Expr:
        args = [self.expr(a, DOUBLE) for a in node.args]
        if node.keywords:
            raise self.fail(node, "keyword arguments to math functions are not supported")
        codes = [a.code for a in args]
        if name in MATH_FUNCS or name in MATH_RENAMED:
            return Expr(f"Math.{MATH_RENAMED.get(name, name)}({', '.join(codes)})", DOUBLE)
        if name == "log":
            if len(codes) == 2:
                return Expr(f"(Math.log({codes[0]}) / Math.log({codes[1]}))", DOUBLE)
            return Expr(f"Math.log({codes[0]})", DOUBLE)
        if name in ("floor", "ceil", "trunc"):
            if name == "trunc":
                return Expr(f"(int) {_paren(args[0], PREC_UNARY)}", INT, PREC_UNARY)
            return Expr(f"(int) Math.{name}({codes[0]})", INT, PREC_UNARY)
        if name == "isclose":
            return Expr(f"(Math.abs({codes[0]} - {codes[1]}) <= 1e-9 * Math.max(Math.abs({codes[0]}), Math.abs({codes[1]})))", BOOLEAN)
        if name == "isnan":
            return Expr(f"Double.isNaN({codes[0]})", BOOLEAN)
        raise self.fail(node, f"math.{name} is not supported")


# ---------------------------------------------------------------- helpers

def _ident(name: str) -> str:
    return name + "_" if name in JAVA_KEYWORDS else name


def _literal(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif ord(ch) < 32 or ord(ch) > 126:
            out.append(f"\\u{ord(ch):04x}" if ord(ch) < 0x10000 else ch)
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def _paren(e: Expr, min_prec: int) -> str:
    return f"({e.code})" if e.prec < min_prec else e.code


def _default(t: JType) -> str:
    u = t
    if u.dims == 0 and u.name == "boolean":
        return "false"
    if u.dims == 0 and u.name in ("double",):
        return "0.0"
    if u.dims == 0 and u.name in ("int", "long", "short", "byte", "float", "char"):
        return "0"
    return "null"


def _widen(known: JType | None, new: JType) -> JType:
    if known is None or known.is_unknown or known == NULL:
        return new
    if new.is_unknown or new == NULL:
        return known
    if known.is_numeric and new.is_numeric and known.is_primitive and new.is_primitive:
        return local_type(numeric_promote(known, new))
    return known


def _const_int(node: ast.expr) -> int | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _const_int(node.operand)
        return -v if v is not None else None
    return None


def _java_format(spec: str, t: JType, node: ast.AST) -> str:
    m = re.fullmatch(r"([<>^]?)(\+?)(0?)(\d*)(?:\.(\d+))?([dfeEgs%]?)", spec)
    if m is None:
        raise Unsupported(node, f"unsupported format spec '{spec}'")
    align, plus, zero, width, prec, kind = m.groups()
    if align == "^":
        raise Unsupported(node, "centered alignment is not supported")
    flags = ("-" if align == "<" else "") + plus + zero
    if not kind:
        kind = "f" if prec else ("d" if t.unboxed().is_integral else "s")
    if kind == "%":
        raise Unsupported(node, "percent format is not supported")
    if kind == "g":
        kind = "g"
    return f"%{flags}{width}{('.' + prec) if prec else ''}{kind}"


def _comments(source: str) -> dict[int, tuple[str, bool]]:
    out: dict[int, tuple[str, bool]] = {}
    code_lines: set[int] = set()
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError):
        return out
    for tok in tokens:
        if tok.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
                            tokenize.ENDMARKER, tokenize.ENCODING):
            for ln in range(tok.start[0], tok.end[0] + 1):
                code_lines.add(ln)
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            raw = tok.string[1:].rstrip() if not tok.string.startswith("#!") else ""
            text = raw[1:] if raw.startswith(" ") else raw  # keep indentation inside the comment
            ln = tok.start[0]
            if text.lstrip().startswith(("type:", "pyright:", "noqa")):
                continue
            out[ln] = (text, ln in code_lines)
    return out


def _walk_function(fn: ast.FunctionDef) -> Iterable[ast.AST]:
    """ast.walk that does not descend into nested functions or lambdas."""
    stack: list[ast.AST] = list(ast.iter_child_nodes(fn))
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        stack.extend(ast.iter_child_nodes(node))


def _shallow_parts(s: ast.stmt) -> list[ast.AST]:
    """Expression parts of a statement, excluding nested statement blocks."""
    parts: list[ast.AST] = []
    for fname, value in ast.iter_fields(s):
        if fname in ("body", "orelse", "finalbody", "handlers"):
            continue
        if isinstance(s, ast.For) and fname == "target":
            continue
        if isinstance(value, ast.AST):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(v for v in value if isinstance(v, ast.AST))
    return parts


def _for_target_name(s: ast.For) -> str | None:
    return s.target.id if isinstance(s.target, ast.Name) else None


def _common_prefix(paths: list[tuple[Any, ...]]) -> tuple[Any, ...]:
    if not paths:
        return ()
    prefix = paths[0]
    for p in paths[1:]:
        i = 0
        while i < len(prefix) and i < len(p) and prefix[i] == p[i]:
            i += 1
        prefix = prefix[:i]
    return prefix


def _loop_between(uses: list[tuple[tuple[Any, ...], bool, ast.stmt]], decl_path: tuple[Any, ...]) -> bool:
    """A use nested deeper than the declaration is fine. Nothing else to check:
    Java rejects uses before declaration, and those are already excluded."""
    return False


def _is_main_guard(node: ast.If) -> bool:
    t = node.test
    return (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name) and t.left.id == "__name__")


def _unsupported_expr_message(node: ast.AST) -> str:
    return {
        "Tuple": "tuples are not supported (Java has no tuples); use a small class or separate variables",
        "ListComp": "list comprehensions are not supported; use a for loop",
        "DictComp": "dict comprehensions are not supported; use a for loop",
        "SetComp": "sets are not supported",
        "Set": "sets are not supported",
        "GeneratorExp": "generator expressions are not supported; use a for loop",
        "NamedExpr": "the walrus operator := is not supported",
        "Await": "async code is not supported",
        "Yield": "generators are not supported",
        "YieldFrom": "generators are not supported",
        "Starred": "*unpacking is not supported",
        "Slice": "slices are not supported",
    }.get(type(node).__name__, f"unsupported expression: {type(node).__name__}")


def collect_sources(root: Path) -> list[Path]:
    skip = {"__pycache__", "node_modules", "venv", ".venv", "env", "ftc", "pyftc", "typings"}
    out = []
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root).parts
        if any(part.startswith(".") or part in skip for part in rel[:-1]) or p.name == "__init__.py":
            continue
        out.append(p)
    return out
