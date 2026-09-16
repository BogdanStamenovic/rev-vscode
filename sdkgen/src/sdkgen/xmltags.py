"""Extracts the `xmlTags` section of Contract 1: every device type that can
appear in a saved robot configuration XML.

Mechanism (see ARCHITECTURE.md): interfaces/classes in the SDK carry a
"flavor" annotation (`MotorType`, `ServoType`, `I2cDeviceType`,
`AnalogSensorType`, `DigitalIoDeviceType`) paired with a `DeviceProperties`
annotation that supplies the actual `xmlTag`. `@Repeatable` lets a single
declaration carry more than one such pair (e.g. `Servo` registers both
"Servo" and "ServoFullRange"); pairs are matched positionally, which is how
the real SDK always writes them (flavor annotation immediately followed,
possibly with unrelated annotations between, by its DeviceProperties).

`LynxUsbDevice` and `LynxModule` are containers with no annotation at all
(they're wired directly into BuiltInConfigurationType) and are added by hand.
"""
from __future__ import annotations

import sys

import javalang.tree as jt

from .registry import Registry, ClassEntry
from .resolve import TypeContext, type_node_to_string, _collect_type_params
from .stringres import resolve_string

FLAVOR_SIMPLE_NAMES = {"MotorType", "ServoType", "I2cDeviceType", "AnalogSensorType", "DigitalIoDeviceType"}
HARDWARE_PKG = "com.qualcomm.robotcore.hardware"


def _ann_simple_name(ann: jt.Annotation) -> str:
    return ann.name.rsplit(".", 1)[-1]


def _literal_to_py(node):
    if node is None:
        return None
    if isinstance(node, jt.Literal):
        v = node.value
        if v is None:
            return None
        if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
            return v[1:-1].encode().decode("unicode_escape")
        if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
            return v[1:-1]
        if v in ("true", "false"):
            return v == "true"
        numeric = v.rstrip("dDfFlL")
        try:
            if numeric.lower().startswith("0x"):
                return int(numeric, 16)
            if "." in numeric or "e" in numeric.lower():
                return float(numeric)
            return int(numeric)
        except ValueError:
            return v
    if isinstance(node, jt.MemberReference) and not node.qualifier:
        return node.member  # bare enum constant, e.g. CW
    if isinstance(node, jt.ElementArrayValue):
        return [_literal_to_py(v) for v in node.values]
    return None


def _resolve_constant_ref(node: jt.MemberReference, ctx: TypeContext, registry: Registry):
    """Resolves `Qualifier.NAME` used as an annotation value. Two cases:
    an enum constant (e.g. `orientation = Rotation.CCW`) -> bare constant
    name; or a `static final` field with a literal initializer (e.g.
    `xmlTag = LynxConstants.EMBEDDED_BHI260AP_IMU_XML_TAG`) -> that literal.
    """
    qualifier = node.qualifier or None
    if qualifier:
        target_fqn = ctx.resolve_simple_name(qualifier)
    else:
        target_fqn = ctx.class_fqn
    if target_fqn is None or target_fqn not in registry.by_fqn:
        return None
    entry = registry.by_fqn[target_fqn]
    if isinstance(entry.node, jt.EnumDeclaration):
        if node.member in {c.name for c in entry.node.body.constants}:
            return node.member
    for fd in getattr(entry.node, "fields", []):
        for decl in fd.declarators:
            if decl.name == node.member and decl.initializer is not None:
                return _literal_to_py(decl.initializer)
    return None


def _element_value_to_py(value, ctx: TypeContext, registry: Registry):
    if isinstance(value, jt.MemberReference) and value.qualifier:
        resolved = _resolve_constant_ref(value, ctx, registry)
        if resolved is not None:
            return resolved
        print(f"sdkgen: could not resolve constant {value.qualifier}.{value.member} "
              f"in {ctx.class_fqn}", file=sys.stderr)
        return f"{value.qualifier}.{value.member}"
    return _literal_to_py(value)


def _annotation_elements(ann: jt.Annotation, ctx: TypeContext, registry: Registry) -> dict:
    elements: dict = {}
    el = ann.element
    if el is None:
        return elements
    if isinstance(el, list):
        for pair in el:
            elements[pair.name] = _element_value_to_py(pair.value, ctx, registry)
    else:
        # Single-value marker annotation, e.g. @SuppressWarnings("x") -> "value"
        elements["value"] = _element_value_to_py(el, ctx, registry)
    return elements


def _strip_generics_and_arrays(type_str: str) -> str:
    return type_str.split("<", 1)[0].rstrip("[]")


def get_hardware_type_name(fqn: str, registry: Registry, _visited: set | None = None) -> str | None:
    """Mirrors NewFile.getHardwareTypeName from OnBotJava: walks up from an
    implementation class to the first type in com.qualcomm.robotcore.hardware
    (interface implemented, else superclass, recursing through superclasses)."""
    if _visited is None:
        _visited = set()
    if fqn in _visited or fqn == "java.lang.Object":
        return None
    _visited.add(fqn)
    entry = registry.by_fqn.get(fqn)
    if entry is None:
        return None
    if entry.package == HARDWARE_PKG:
        return fqn

    node = entry.node
    ctx = TypeContext(registry=registry, class_fqn=fqn,
                       type_param_names=_collect_type_params(getattr(node, "type_parameters", None)))
    if isinstance(node, jt.ClassDeclaration):
        iface_nodes = node.implements or []
        super_node = node.extends
    elif isinstance(node, jt.InterfaceDeclaration):
        iface_nodes = node.extends or []
        super_node = None
    else:
        iface_nodes, super_node = [], None

    for iface in iface_nodes:
        iface_fqn = _strip_generics_and_arrays(type_node_to_string(iface, ctx))
        iface_entry = registry.by_fqn.get(iface_fqn)
        if iface_entry and iface_entry.package == HARDWARE_PKG:
            return iface_fqn

    if super_node is not None:
        super_fqn = _strip_generics_and_arrays(type_node_to_string(super_node, ctx))
        if super_fqn in registry.by_fqn:
            result = get_hardware_type_name(super_fqn, registry, _visited)
            if result:
                return result
    return None


def _category_for_pair(flavor_ann: jt.Annotation | None, javatype_for_custom_servo: str | None) -> str:
    if flavor_ann is None:
        return "other"
    kind = _ann_simple_name(flavor_ann)
    if kind == "MotorType":
        return "motor"
    if kind == "I2cDeviceType":
        return "i2c"
    if kind == "AnalogSensorType":
        return "analog"
    if kind == "DigitalIoDeviceType":
        return "digital"
    if kind == "ServoType":
        return "servo"  # refined by caller for CONTINUOUS/CUSTOM
    return "other"


def extract_xml_tags(registry: Registry, string_resources: dict[str, str]) -> dict:
    tags: dict = {}

    for entry in registry.by_fqn.values():
        node = entry.node
        annotations = list(getattr(node, "annotations", []) or [])
        if not any(_ann_simple_name(a) == "DeviceProperties" for a in annotations):
            continue

        flavor_anns = [a for a in annotations if _ann_simple_name(a) in FLAVOR_SIMPLE_NAMES]
        dp_anns = [a for a in annotations if _ann_simple_name(a) == "DeviceProperties"]

        ctx = TypeContext(registry=registry, class_fqn=entry.fqn,
                           type_param_names=_collect_type_params(getattr(node, "type_parameters", None)))

        pair_count = max(len(flavor_anns), len(dp_anns))
        for i in range(pair_count):
            flavor_ann = flavor_anns[i] if i < len(flavor_anns) else None
            dp_ann = dp_anns[i] if i < len(dp_anns) else None
            if dp_ann is None:
                continue  # a flavor annotation with no DeviceProperties can't register a tag
            dp_elements = _annotation_elements(dp_ann, ctx, registry)
            xml_tag = dp_elements.get("xmlTag")
            if not xml_tag or not isinstance(xml_tag, str):
                print(f"sdkgen: DeviceProperties on {entry.fqn} has no resolvable xmlTag, skipping",
                      file=sys.stderr)
                continue

            flavor_elements = _annotation_elements(flavor_ann, ctx, registry) if flavor_ann else {}
            category = _category_for_pair(flavor_ann, None)

            impl_class = entry.fqn if isinstance(node, jt.ClassDeclaration) else None

            if category == "motor":
                java_type = "com.qualcomm.robotcore.hardware.DcMotor"
                props = {k: v for k, v in flavor_elements.items()}
            elif category == "servo":
                servo_flavor = flavor_elements.get("flavor", "STANDARD")
                if servo_flavor == "CONTINUOUS":
                    category = "crservo"
                    java_type = "com.qualcomm.robotcore.hardware.CRServo"
                elif servo_flavor == "CUSTOM":
                    resolved = get_hardware_type_name(entry.fqn, registry)
                    java_type = resolved or "com.qualcomm.robotcore.hardware.Servo"
                    category = "crservo" if java_type.endswith("CRServo") else "servo"
                else:
                    java_type = "com.qualcomm.robotcore.hardware.Servo"
                props = {k: v for k, v in flavor_elements.items() if k not in ("xmlTag",)}
            else:
                java_type = get_hardware_type_name(entry.fqn, registry)
                if category == "i2c" and java_type is None:
                    # Fall back to the annotated interface itself if it's
                    # already the user-facing hardware interface.
                    java_type = entry.fqn if entry.package == HARDWARE_PKG else None
                if category == "i2c" and _looks_like_imu(entry, registry):
                    category = "imu"
                props = dict(flavor_elements)

            display_name = resolve_string(dp_elements.get("name", xml_tag), string_resources)
            description = dp_elements.get("description")
            if description:
                props = dict(props)
                props["description"] = resolve_string(description, string_resources)

            if xml_tag in tags:
                print(f"sdkgen: duplicate xmlTag {xml_tag!r} ({entry.fqn} vs existing), keeping first",
                      file=sys.stderr)
                continue

            tags[xml_tag] = {
                "javaType": java_type,
                "implClass": impl_class,
                "category": category,
                "displayName": display_name,
                "props": props,
            }

    _add_builtin_tags(tags, registry)
    return tags


def _looks_like_imu(entry: ClassEntry, registry: Registry) -> bool:
    name = entry.simple_name.lower()
    if "imu" in name:
        return True
    node = entry.node
    impls = list(getattr(node, "implements", None) or []) + list(getattr(node, "extends", None) or [] if isinstance(getattr(node, "extends", None), list) else [])
    ext = getattr(node, "extends", None)
    if ext is not None and not isinstance(ext, list):
        impls.append(ext)
    ctx = TypeContext(registry=registry, class_fqn=entry.fqn)
    for t in impls:
        s = _strip_generics_and_arrays(type_node_to_string(t, ctx))
        if s.rsplit(".", 1)[-1] in ("IMU", "BNO055IMU", "BNO055IMUNew"):
            return True
    return False


def _add_builtin_tags(tags: dict, registry: Registry) -> None:
    """LynxUsbDevice and LynxModule are containers wired directly into
    BuiltInConfigurationType with no annotation on any class -- hand-added
    per ARCHITECTURE.md."""
    lynx_module_fqn = "com.qualcomm.hardware.lynx.LynxModule"
    lynx_usb_fqn = "com.qualcomm.hardware.lynx.LynxUsbDevice"

    if "LynxModule" not in tags:
        tags["LynxModule"] = {
            "javaType": lynx_module_fqn if lynx_module_fqn in registry.by_fqn else None,
            "implClass": lynx_module_fqn if lynx_module_fqn in registry.by_fqn else None,
            "category": "other",
            "displayName": "Expansion Hub",
            "props": {},
        }
    if "LynxUsbDevice" not in tags:
        java_type = lynx_usb_fqn if lynx_usb_fqn in registry.by_fqn else None
        tags["LynxUsbDevice"] = {
            "javaType": java_type,
            "implClass": java_type,
            "category": "other",
            "displayName": "Lynx USB Device",
            "props": {},
        }
