from deck import theme


def test_canvas_avoids_slide_number_placeholder():
    left, top, width, height = theme.CANVAS
    assert (left, top) == (0.26, 0.65)
    assert left + width <= 7.24
    # 0.65 + 4.45 is not exactly 5.10 in IEEE 754 binary floating point; allow 1e-9 tolerance
    assert top + height <= 5.10 + 1e-9


def test_palette_exact_values():
    assert str(theme.PRIMARY) == "4285F4"
    assert str(theme.WARM) == "FFAB40"
    assert str(theme.TEAL) == "0097A7"
    assert str(theme.MUTED) == "595959"


def test_placeholder_sizes_match_the_template():
    # measured from template.pptx; layouts that inherit 10.5pt get an override
    assert theme.PLACEHOLDER_PT[("BIG_NUMBER", 0)] == 90.0
    assert theme.PLACEHOLDER_PT[("MAIN_POINT", 0)] == 36.0
    assert theme.PLACEHOLDER_PT[("TITLE", 0)] == 31.5
    assert theme.PLACEHOLDER_PT[("SECTION_HEADER", 0)] == 27.0
    assert theme.PLACEHOLDER_PT[("TITLE_ONLY", 0)] == 20.0
    assert theme.PLACEHOLDER_PT[("BIG_NUMBER", 1)] == 14.0


def test_big_number_budget_flags_long_figures():
    chars_per_line, lines, total = theme.budget(6.99, 2.15, 90.0)
    assert chars_per_line == 10
    assert lines == 1
    assert total == 10
    assert theme.wrapped_lines("883,599,352", chars_per_line) > lines


def test_monospace_budget_is_wider_per_character():
    _, _, proportional = theme.budget(6.0, 3.0, 12.0)
    _, _, monospace = theme.budget(6.0, 3.0, 12.0, mono=True)
    assert monospace < proportional


def test_wrapped_lines_counts_explicit_newlines():
    assert theme.wrapped_lines("a\nb\nc", 40) == 3
    assert theme.wrapped_lines("x" * 81, 40) == 3
