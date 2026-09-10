"""Pre-write validation: text fit, redaction, notes, and timing."""

import collections
import re
import zipfile

from deck import shapes, slides, theme

Violation = collections.namedtuple("Violation", "slide_index kind detail")

BANNED = (
    "ete-litellm",
    "NEO4J_PASSWORD",
    "concert-juice-shop-demo",
    "concert_assessment_id",
    "Concert",
    "/Users/rkrsn",
)

# Prompt text the template's own layouts carry. If any of these reaches a
# rendered slide, a placeholder shipped unfilled. Measured from template.pptx:
# BIG_NUMBER idx 0 prompts "xx%", and every layout's idx 12 prompts the
# slide-number glyph. These are matched only against ppt/slides/slideN.xml,
# never the layouts or masters, where they are supposed to appear.
PLACEHOLDER_PROMPTS = ("xx%", "\u2039#\u203a", "Lorem", "lorem", "ipsum")
SLIDE_PART = re.compile(r"^ppt/slides/slide\d+\.xml$")

NOTES_MARKER = re.compile(r"^\[(\d+)s\]")


def _fit_violations(index, slide_spec):
    out = []
    for (layout, idx), field_name in slides.PLACEHOLDER_FIELD.items():
        if layout != slide_spec.layout:
            continue
        text = getattr(slide_spec, field_name, "")
        if not text:
            continue
        _, _, width, height = theme.PLACEHOLDER_BOX[(layout, idx)]
        pt = slides.point_size(layout, idx, slide_spec.pt_override)
        chars_per_line, max_lines, _ = theme.budget(width, height, pt)
        used = theme.wrapped_lines(text, chars_per_line)
        if used > max_lines:
            out.append(
                Violation(
                    index,
                    "overflow",
                    f"{layout} idx{idx} at {pt}pt needs {used} lines, "
                    f"box holds {max_lines}: {text[:60]!r}",
                )
            )
    return out


def _shape_cells(shape):
    """Yield (label, text, width_in, height_in, pt, mono) per budgeted unit
    of a composed shape: one per table cell, one per box label, one for a
    code block, one per key/value in a KeyValues row."""
    if isinstance(shape, shapes.Table):
        n_rows = len(shape.rows)
        n_cols = len(shape.rows[0]) if n_rows else 0
        cell_w = shape.width / n_cols if n_cols else shape.width
        cell_h = shape.height / n_rows if n_rows else shape.height
        for r, row in enumerate(shape.rows):
            for c, value in enumerate(row):
                yield (f"Table row{r} col{c}", str(value), cell_w, cell_h, shape.pt, False)
    elif isinstance(shape, shapes.Boxes):
        count = len(shape.labels)
        gap = 0.18 if shape.arrows and count > 1 else 0.08
        box_w = (shape.width - gap * (count - 1)) / count if count else shape.width
        for i, label in enumerate(shape.labels):
            yield (f"Boxes label{i}", str(label), box_w, shape.height, shape.pt, False)
    elif isinstance(shape, shapes.Code):
        yield ("Code", shape.text, shape.width, shape.height, shape.pt, True)
    elif isinstance(shape, shapes.KeyValues):
        key_w = shape.width * shape.key_fraction
        value_w = shape.width - key_w
        row_h = shape.height / max(1, len(shape.pairs))
        for i, (key, value) in enumerate(shape.pairs):
            yield (f"KeyValues row{i} key", str(key), key_w, row_h, shape.pt, True)
            yield (f"KeyValues row{i} value", str(value), value_w, row_h, shape.pt, True)


def _shape_violations(index, slide_spec):
    out = []
    for shape in slide_spec.shapes:
        for label, text, width, height, pt, mono in _shape_cells(shape):
            if not text:
                continue
            chars_per_line, max_lines, _ = theme.budget(width, height, pt, mono=mono)
            used = theme.wrapped_lines(text, chars_per_line)
            if used > max_lines:
                out.append(
                    Violation(
                        index,
                        "overflow",
                        f"{label} at {pt}pt needs {used} lines, "
                        f"box holds {max_lines}: {text[:60]!r}",
                    )
                )
    return out


def _text_of(slide_spec):
    return "\n".join(
        [
            slide_spec.title,
            slide_spec.subtitle,
            slide_spec.body,
            slide_spec.big,
            slide_spec.caption,
            slide_spec.notes,
        ]
        + [getattr(s, "text_for_check", "") for s in slide_spec.shapes]
    )


def check_slides(section_slides):
    """Return every violation across a list of Slide descriptors."""
    out = []
    for index, slide_spec in enumerate(section_slides, start=1):
        out.extend(_fit_violations(index, slide_spec))
        out.extend(_shape_violations(index, slide_spec))

        match = NOTES_MARKER.match(slide_spec.notes or "")
        if not match:
            out.append(
                Violation(
                    index,
                    "notes",
                    "notes missing or not starting with a [<seconds>s] marker",
                )
            )
        elif int(match.group(1)) != slide_spec.seconds:
            out.append(
                Violation(
                    index,
                    "timing",
                    f"notes say {match.group(1)}s, seconds field says "
                    f"{slide_spec.seconds}",
                )
            )

        text = _text_of(slide_spec)
        for banned in BANNED:
            if banned in text:
                out.append(Violation(index, "redaction", f"{banned!r} in slide text"))
    return out


def check_output(pptx_path):
    """Scan a saved deck's XML for banned strings and unfilled placeholders."""
    out = []
    with zipfile.ZipFile(pptx_path) as zf:
        for name in zf.namelist():
            if not name.endswith(".xml"):
                continue
            blob = zf.read(name).decode("utf-8", "replace")
            for banned in BANNED:
                if banned in blob:
                    out.append(Violation(0, "redaction", f"{banned!r} in {name}"))
            if SLIDE_PART.match(name):
                for prompt in PLACEHOLDER_PROMPTS:
                    if prompt in blob:
                        out.append(
                            Violation(0, "placeholder", f"{prompt!r} in {name}")
                        )
    return out


def report(violations):
    """Human-readable summary. Returns True when clean."""
    if not violations:
        print("checks: clean")
        return True
    for violation in violations:
        print(f"  slide {violation.slide_index}: {violation.kind}: {violation.detail}")
    print(f"checks: {len(violations)} violation(s)")
    return False
