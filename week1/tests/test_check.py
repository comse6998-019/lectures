from deck import check, slides


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
