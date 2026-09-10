from deck import check, slides
from deck.shapes import Boxes, Code, KeyValues, Table


def test_clean_slide_has_no_violations():
    result = check.check_slides(
        [slides.Slide(layout="SECTION_HEADER", title="Anatomy", notes="[30s] x", seconds=30)]
    )
    assert result == []


def test_overlong_big_number_is_flagged():
    result = check.check_slides(
        [
            slides.Slide(
                layout="BIG_NUMBER",
                big="883,599,352",
                body="cache_read tokens",
                notes="[60s] x",
                seconds=60,
            )
        ]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "BIG_NUMBER" in result[0].detail and "883,599,352" in result[0].detail


def test_overlong_big_number_passes_with_size_override():
    result = check.check_slides(
        [
            slides.Slide(
                layout="BIG_NUMBER",
                big="883,599,352",
                body="cache_read tokens",
                pt_override={0: 48.0},
                notes="[60s] x",
                seconds=60,
            )
        ]
    )
    assert result == []


def test_placeholder_inset_flags_a_two_line_title_that_used_to_fit():
    # SECTION_HEADER_1 idx0's declared box (6.99x0.92in at 27pt) budgets 2
    # lines with no inset subtracted. The template's own bodyPr inset on
    # this placeholder shrinks the real text area to ~6.78x0.71in, which
    # only holds 1 line. Two short hard lines that each fit their own
    # width on their own still overflow the line count once the inset is
    # subtracted.
    result = check.check_slides(
        [
            slides.Slide(
                layout="SECTION_HEADER_1",
                title="First short line\nSecond short line",
                notes="[10s] x",
                seconds=10,
            )
        ]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "SECTION_HEADER_1" in result[0].detail


def test_composed_shape_that_fits_has_no_violations():
    table = Table(
        rows=[["A", "B"], ["ok", "also fine"]],
        left=0.2,
        top=0.2,
        width=3,
        height=1,
        pt=10,
    )
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[table], notes="[10s] x", seconds=10)]
    )
    assert result == []


def test_table_flags_a_single_overlong_cell_in_an_otherwise_fine_table():
    table = Table(
        rows=[
            ["A", "B"],
            ["ok", "this text is quite long for such a small cell width"],
        ],
        left=0,
        top=0,
        width=2,
        height=1,
        pt=10,
    )
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[table], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "Table row1 col1" in result[0].detail


def test_boxes_flags_an_overlong_label():
    boxes = Boxes(
        labels=["ok", "this is a very long label text that will not fit"],
        left=0,
        top=0,
        width=2,
        height=0.3,
        pt=11,
    )
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[boxes], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "Boxes label1" in result[0].detail


def test_code_flags_overlong_text():
    code = Code(text="x" * 300, left=0, top=0, width=1, height=0.3, pt=11)
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[code], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "Code" in result[0].detail


def test_keyvalues_flags_an_overlong_value():
    kv = KeyValues(
        pairs=[
            ("key1", "short"),
            (
                "key2",
                "this value text is intentionally far too long to fit "
                "in the small value box provided",
            ),
        ],
        left=0,
        top=0,
        width=2,
        height=0.4,
        pt=12,
    )
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[kv], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "KeyValues row1 value" in result[0].detail


def test_table_margin_gap_flags_a_cell_a_no_margin_budget_would_miss():
    # Each table cell keeps python-pptx's default 0.1in/0.05in text-frame
    # inset. A 1x0.4in cell (width=2, height=0.4, 2 cols, 1 row) budgets to
    # (13 chars, 2 lines) with no margin subtracted, and a 20-char cell
    # fits (20 <= 26 chars of capacity) — but the real text area is only
    # 0.8x0.3in, budgeting to (10, 1): 20 chars needs 2 lines, box holds 1.
    table = Table(rows=[["short", "x" * 20]], left=0, top=0, width=2, height=0.4, pt=10)
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[table], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "Table row0 col1" in result[0].detail


def test_code_no_wrap_flags_a_line_a_wrap_model_would_miss():
    # Code.draw sets word_wrap = False, so a 36-char single line never
    # wraps onto a second line. The wrap model would greedily wrap it to
    # 3 lines against a 3-line box and call it clean; rendered, it is one
    # 36-char line that overruns a 10-char-wide box.
    code = Code(text="x" * 36, left=0, top=0, width=1.2, height=0.6, pt=11)
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[code], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "Code" in result[0].detail and "no wrap" in result[0].detail


def test_code_overflow_depends_on_the_mono_advance_constant():
    # At this box (2x0.3in, 11pt), the real mono capacity is 19 chars/line
    # but the proportional advance would wrongly allow 21. A 20-char line
    # overflows under the correct mono budget and would pass silently if
    # Code were ever budgeted as proportional instead.
    code = Code(text="x" * 20, left=0, top=0, width=2, height=0.3, pt=11)
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[code], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "Code" in result[0].detail


def test_keyvalues_overflow_depends_on_the_mono_advance_constant():
    # Value box here budgets to 12 chars/line under the correct mono
    # advance but 13 under proportional. A 13-char value overflows only
    # under the correct budget, so it would pass silently under the wrong
    # one.
    kv = KeyValues(
        pairs=[("key", "0123456789abc")], left=0, top=0, width=2.5, height=0.5, pt=12
    )
    result = check.check_slides(
        [slides.Slide(layout="BLANK", shapes=[kv], notes="[10s] x", seconds=10)]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "KeyValues row0 value" in result[0].detail


def test_missing_notes_is_flagged():
    result = check.check_slides([slides.Slide(layout="BLANK", seconds=10)])
    assert "notes" in [v.kind for v in result]


def test_notes_must_start_with_a_seconds_marker():
    result = check.check_slides(
        [slides.Slide(layout="BLANK", notes="say the thing", seconds=10)]
    )
    assert "notes" in [v.kind for v in result]


def test_notes_seconds_must_match_the_seconds_field():
    result = check.check_slides(
        [slides.Slide(layout="BLANK", notes="[45s] x", seconds=30)]
    )
    assert "timing" in [v.kind for v in result]


def test_redacted_string_in_slide_text_is_flagged():
    result = check.check_slides(
        [
            slides.Slide(
                layout="SECTION_HEADER",
                title="run under /Users/rkrsn/workspace",
                notes="[10s] x",
                seconds=10,
            )
        ]
    )
    assert "redaction" in [v.kind for v in result]


def test_check_output_scans_saved_xml(tmp_path):
    import pathlib

    template = pathlib.Path(__file__).parent.parent.parent / "template.pptx"
    prs = slides.build(
        template,
        [
            slides.Slide(
                layout="SECTION_HEADER",
                title="clean",
                notes="[10s] x",
                seconds=10,
            )
        ],
    )
    out = tmp_path / "clean.pptx"
    prs.save(out)
    assert check.check_output(out) == []


def test_check_output_finds_banned_string_in_saved_xml(tmp_path):
    import pathlib

    template = pathlib.Path(__file__).parent.parent.parent / "template.pptx"
    prs = slides.build(
        template,
        [
            slides.Slide(
                layout="SECTION_HEADER",
                title="NEO4J_PASSWORD leaked here",
                notes="[10s] x",
                seconds=10,
            )
        ],
    )
    out = tmp_path / "leaky.pptx"
    prs.save(out)
    result = check.check_output(out)
    assert [v.kind for v in result] == ["redaction"]
    assert "NEO4J_PASSWORD" in result[0].detail


def test_check_output_finds_placeholder_in_saved_xml(tmp_path):
    import pathlib

    template = pathlib.Path(__file__).parent.parent.parent / "template.pptx"
    prs = slides.build(
        template,
        [
            slides.Slide(
                layout="TITLE_ONLY",
                title="Lorem",
                notes="[10s] x",
                seconds=10,
            )
        ],
    )
    out = tmp_path / "placeholder.pptx"
    prs.save(out)
    result = check.check_output(out)
    assert any(v.kind == "placeholder" for v in result)
    placeholder_violations = [v for v in result if v.kind == "placeholder"]
    assert len(placeholder_violations) == 1
    assert "Lorem" in placeholder_violations[0].detail
