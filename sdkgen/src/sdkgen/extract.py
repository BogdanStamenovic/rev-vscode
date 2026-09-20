"""Builds the Contract-1 `classes` dict from the parsed registry."""
from __future__ import annotations

import re

import javalang.tree as jt

from .javadoc import clean_javadoc
from .registry import Registry, ClassEntry
from .resolve import TypeContext, type_node_to_string, type_params_to_strings, _collect_type_params

_FQN_TOKEN_RE = re.compile(r"[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*")

KIND_BY_NODE = {
    jt.ClassDeclaration: "class",
    jt.InterfaceDeclaration: "interface",
    jt.EnumDeclaration: "enum",
    jt.AnnotationDeclaration: "annotation",
}


def collect_referenced_fqns(type_str: str, registry: Registry) -> set[str]:
    found = set()
    for token in _FQN_TOKEN_RE.findall(type_str):
        parts = token.split(".")
        for i in range(len(parts), 0, -1):
            candidate = ".".join(parts[:i])
            if candidate in registry.by_fqn:
                found.add(candidate)
    return found


def _is_private(modifiers) -> bool:
    return "private" in (modifiers or ())


def _get_extends_list(node) -> list:
    exts = []
    ext = getattr(node, "extends", None)
    if ext:
        if isinstance(ext, list):
            exts.extend(ext)
        else:
            exts.append(ext)
    impl = getattr(node, "implements", None)
    if impl:
        exts.extend(impl)
    return exts


def _method_to_dict(m, ctx: TypeContext, referenced: set[str], registry: Registry) -> dict:
    method_type_params = _collect_type_params(m.type_parameters)
    inner_ctx = TypeContext(registry=ctx.registry, class_fqn=ctx.class_fqn,
                             type_param_names=ctx.type_param_names | method_type_params)
    params = []
    for p in m.parameters:
        t = type_node_to_string(p.type, inner_ctx)
        referenced |= collect_referenced_fqns(t, registry)
        params.append({"name": p.name, "type": t, "varargs": bool(p.varargs)})
    returns = type_node_to_string(m.return_type, inner_ctx)
    referenced |= collect_referenced_fqns(returns, registry)
    first_doc, _ = clean_javadoc(m.documentation)
    return {
        "name": m.name,
        "static": "static" in m.modifiers,
        "abstract": m.body is None,
        "typeParams": type_params_to_strings(m.type_parameters, inner_ctx),
        "params": params,
        "returns": returns,
        "doc": first_doc,
    }


def _ctor_to_dict(c, ctx: TypeContext, referenced: set[str], registry: Registry) -> dict:
    params = []
    for p in c.parameters:
        t = type_node_to_string(p.type, ctx)
        referenced |= collect_referenced_fqns(t, registry)
        params.append({"name": p.name, "type": t, "varargs": bool(p.varargs)})
    first_doc, _ = clean_javadoc(c.documentation)
    return {"params": params, "doc": first_doc}


def _field_to_dict(fd, declarator, ctx: TypeContext, referenced: set[str], registry: Registry,
                    force_static_final: bool = False) -> dict:
    t = type_node_to_string(fd.type, ctx)
    extra_dims = len(getattr(declarator, "dimensions", None) or [])
    if extra_dims:
        t = t + ("[]" * extra_dims)
    referenced |= collect_referenced_fqns(t, registry)
    first_doc, _ = clean_javadoc(fd.documentation)
    return {
        "name": declarator.name,
        "type": t,
        # JLS 9.3: every field declared in the body of an interface is
        # implicitly public, static and final, whether or not the source
        # spells out the modifiers (and FTC SDK interfaces routinely don't,
        # e.g. `double MAX_POSITION = 1.0;` inside `interface Servo`).
        # javalang's `modifiers` only reports what's written, so a plain
        # `"static" in fd.modifiers` check misses every one of these --
        # `force_static_final` (set from the enclosing type's kind, below)
        # is what makes ClassName.CONSTANT resolve as the static access it
        # actually is instead of translating into a javac error.
        "static": force_static_final or "static" in fd.modifiers,
        "final": force_static_final or "final" in fd.modifiers,
        "doc": first_doc,
    }


def extract_full(entry: ClassEntry, registry: Registry, module: str | None,
                  referenced: set[str]) -> dict:
    node = entry.node
    kind = KIND_BY_NODE[type(node)]
    class_type_params = _collect_type_params(getattr(node, "type_parameters", None))
    ctx = TypeContext(registry=registry, class_fqn=entry.fqn, type_param_names=class_type_params)

    extends_strs = []
    for ext_node in _get_extends_list(node):
        s = type_node_to_string(ext_node, ctx)
        referenced |= collect_referenced_fqns(s, registry)
        extends_strs.append(s)

    if kind == "annotation":
        # Annotation elements aren't MethodDeclaration nodes in javalang; we
        # model them as fields (name + declared type) since Contract 1 has
        # no dedicated "elements" key. Documented deviation.
        fields = []
        for elem in node.body:
            t = type_node_to_string(elem.return_type, ctx)
            referenced |= collect_referenced_fqns(t, registry)
            fields.append({"name": elem.name, "type": t, "static": False, "final": False, "doc": ""})
        methods, ctors, enum_constants = [], [], []
        abstract = False
    else:
        methods = [_method_to_dict(m, ctx, referenced, registry)
                   for m in node.methods if not _is_private(m.modifiers)]
        ctors = [_ctor_to_dict(c, ctx, referenced, registry)
                 for c in node.constructors if not _is_private(c.modifiers)]
        fields = []
        for fd in node.fields:
            if _is_private(fd.modifiers):
                continue
            for decl in fd.declarators:
                fields.append(_field_to_dict(fd, decl, ctx, referenced, registry, force_static_final=(kind == "interface")))
        enum_constants = [c.name for c in node.body.constants] if kind == "enum" else []
        if kind == "interface":
            abstract = True
        else:
            abstract = "abstract" in getattr(node, "modifiers", set())

    first_doc, _ = clean_javadoc(node.documentation)

    return {
        "kind": kind,
        "simpleName": entry.simple_name,
        "outer": entry.outer_fqn,
        "module": module,
        "typeParams": type_params_to_strings(getattr(node, "type_parameters", None), ctx),
        "extends": extends_strs,
        "abstract": abstract,
        "methods": methods,
        "constructors": ctors,
        "fields": fields,
        "enumConstants": enum_constants,
        "doc": first_doc,
    }
