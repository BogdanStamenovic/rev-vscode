"""Javadoc comment -> plain text, for Contract 1 `doc` fields and Python
docstrings.
"""
from __future__ import annotations

import re

_TAG_RE = re.compile(r"<[^>]+>")
_LINK_RE = re.compile(r"\{@link\s+([^}]+)\}")
_CODE_RE = re.compile(r"\{@code\s+([^}]+)\}")
_OTHER_INLINE_TAG_RE = re.compile(r"\{@\w+\s+([^}]*)\}")
_LEADING_STAR_RE = re.compile(r"^\s*\*\s?", re.MULTILINE)


def _strip_comment_delimiters(raw: str) -> str:
    text = raw.strip()
    if text.startswith("/**"):
        text = text[3:]
    elif text.startswith("/*"):
        text = text[2:]
    if text.endswith("*/"):
        text = text[:-2]
    text = _LEADING_STAR_RE.sub("", text)
    return text


def _clean_inline_markup(text: str) -> str:
    # {@link com.foo.Bar#baz(int)} -> com.foo.Bar#baz(int) -> simplified to last segment on the '#'
    def link_sub(m: re.Match) -> str:
        target = m.group(1).strip()
        # Drop a leading '#' (self-reference) and any javadoc label after whitespace.
        target = target.split()[0] if target else target
        return target

    text = _LINK_RE.sub(link_sub, text)
    text = _CODE_RE.sub(lambda m: m.group(1).strip(), text)
    text = _OTHER_INLINE_TAG_RE.sub(lambda m: m.group(1).strip(), text)
    text = _TAG_RE.sub("", text)
    return text


def _split_body_and_block_tags(text: str) -> tuple[str, list[str]]:
    """Separates the free-text body from trailing @tag lines (e.g. @param,
    @return, @see, @deprecated)."""
    lines = text.split("\n")
    body_lines: list[str] = []
    tag_lines: list[str] = []
    in_tags = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@"):
            in_tags = True
        if in_tags:
            tag_lines.append(stripped)
        else:
            body_lines.append(line)
    return "\n".join(body_lines).strip(), tag_lines


def clean_javadoc(raw: str | None) -> tuple[str, str]:
    """Returns (first_paragraph, extended) both as plain text with HTML/
    {@link}/{@code} stripped. `extended` is first ~3 paragraphs + @param
    lines, for Python docstrings; `first_paragraph` is for Contract 1 `doc`.
    """
    if not raw:
        return "", ""
    text = _strip_comment_delimiters(raw)
    text = _clean_inline_markup(text)
    body, tag_lines = _split_body_and_block_tags(text)

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    # Javadoc allows single blank-less newlines within a paragraph; collapse
    # internal whitespace/newlines to single spaces per paragraph.
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in paragraphs]

    first_paragraph = paragraphs[0] if paragraphs else ""

    extended_parts = list(paragraphs[:3])
    param_lines = [t for t in tag_lines if t.startswith("@param") or t.startswith("@return")]
    if param_lines:
        extended_parts.append("\n".join(param_lines))
    extended = "\n\n".join(extended_parts).strip()

    return first_paragraph, extended
