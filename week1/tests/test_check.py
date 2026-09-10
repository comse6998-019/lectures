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
