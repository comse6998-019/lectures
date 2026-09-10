"""Section registry. Each section is a module returning a list of Slides."""

import collections
import functools
import importlib
import json
import pathlib

Section = collections.namedtuple(
    "Section", "key module_name start_min end_min expected_slides"
)

SECTIONS = (
    Section("welcome", "s01_welcome", 0, 3, 3),
    Section("why", "s02_why", 3, 13, 9),
    Section("history", "s03_history", 13, 19, 5),
    Section("logistics", "s04_logistics", 19, 26, 7),
    Section("anatomy", "s05_anatomy", 26, 45, 16),
    Section("unit1", "s06_unit1", 45, 54, 7),
    Section("unit2", "s07_unit2", 54, 66, 8),
    Section("unit3", "s08_unit3", 66, 75, 7),
    Section("unit4", "s09_unit4", 75, 84, 7),
    Section("job", "s10_job", 84, 90, 6),
    Section("homeworks", "s11_homeworks", 90, 97, 6),
    Section("trace", "s12_trace", 97, 108, 14),
    Section("next", "s13_next", 108, 110, 2),
    Section("appendix", "s14_appendix", None, None, 16),
)

# unit2 runs 54-66 because its last slide is the three-minute break. Keeping the
# break inside a section is what makes the timeline contiguous and sum to 110.

FIGURES_PATH = pathlib.Path(__file__).parent.parent / "data" / "figures.json"


@functools.cache
def figures():
    return json.loads(FIGURES_PATH.read_text())


def load(key):
    section = next(s for s in SECTIONS if s.key == key)
    module = importlib.import_module(f"content.{section.module_name}")
    return module.slides()


def all_slides():
    out = []
    for section in SECTIONS:
        try:
            out.extend(load(section.key))
        except ModuleNotFoundError:
            continue  # section not implemented yet
    return out
