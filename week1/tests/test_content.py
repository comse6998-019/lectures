import pytest

import content


def test_all_slides_skips_a_section_whose_module_is_genuinely_absent(monkeypatch):
    missing = content.Section("nope", "s99_does_not_exist", 0, 1, 1)
    monkeypatch.setattr(content, "SECTIONS", content.SECTIONS + (missing,))
    slides, skipped = content.all_slides()
    assert "nope" in skipped
    assert isinstance(slides, list)


def test_all_slides_raises_when_a_present_sections_own_import_is_broken(
    monkeypatch, tmp_path
):
    (tmp_path / "broken_section.py").write_text(
        "import this_inner_module_does_not_exist\n\n\ndef slides():\n    return []\n"
    )
    monkeypatch.setattr(content, "__path__", list(content.__path__) + [str(tmp_path)])
    broken = content.Section("broken", "broken_section", 0, 1, 1)
    monkeypatch.setattr(content, "SECTIONS", content.SECTIONS + (broken,))
    with pytest.raises(ModuleNotFoundError) as exc_info:
        content.all_slides()
    assert exc_info.value.name == "this_inner_module_does_not_exist"


def test_sections_are_contiguous_and_sum_to_110_minutes():
    timed = [s for s in content.SECTIONS if s.start_min is not None]
    assert timed[0].start_min == 0
    assert timed[-1].end_min == 110
    for earlier, later in zip(timed, timed[1:]):
        assert earlier.end_min == later.start_min, (earlier.key, later.key)
    assert sum(s.end_min - s.start_min for s in timed) == 110


def test_the_break_falls_on_the_midterm_final_seam():
    by_key = {s.key: s for s in content.SECTIONS}
    # units 1-2 are the midterm material, units 3-4 the final; the break divides
    # them, and lives at the end of unit2 so the timeline stays contiguous
    assert by_key["unit2"].end_min == 66
    assert by_key["unit3"].start_min == 66
    try:
        unit2 = content.load("unit2")
    except ModuleNotFoundError:
        return
    last = unit2[-1]
    assert last.layout == "SECTION_HEADER_1"
    assert last.seconds == 180


def test_slide_budget_totals_match_the_spec():
    timed = sum(s.expected_slides for s in content.SECTIONS if s.start_min is not None)
    appendix = sum(
        s.expected_slides for s in content.SECTIONS if s.start_min is None
    )
    assert timed == 97
    assert appendix == 16


def test_figures_load():
    figures = content.figures()
    assert figures["tally"]["total"] == 22


def test_each_implemented_section_matches_its_expected_slide_count():
    for section in content.SECTIONS:
        try:
            loaded = content.load(section.key)
        except ModuleNotFoundError:
            continue  # not yet implemented
        assert len(loaded) == section.expected_slides, section.key


def test_each_implemented_sections_seconds_fit_its_minutes():
    for section in content.SECTIONS:
        if section.start_min is None:
            continue
        try:
            loaded = content.load(section.key)
        except ModuleNotFoundError:
            continue
        budget = (section.end_min - section.start_min) * 60
        spent = sum(s.seconds for s in loaded)
        assert spent <= budget, f"{section.key}: {spent}s over {budget}s"
        assert spent >= budget * 0.85, f"{section.key}: only {spent}s of {budget}s"
