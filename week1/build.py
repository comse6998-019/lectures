#!/usr/bin/env python3
"""Build the Lecture 1 deck.

  python3 build.py                 build everything to out/lecture-01.pptx
  python3 build.py --only anatomy  build one section to out/section-anatomy.pptx
  python3 build.py --check-only    validate without writing
"""

import argparse
import pathlib
import sys

import content
from deck import check, slides

HERE = pathlib.Path(__file__).parent
TEMPLATE = HERE.parent / "template.pptx"
OUT_DIR = HERE / "out"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="section key to build alone")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)

    if args.only:
        section_slides = content.load(args.only)
        out_path = OUT_DIR / f"section-{args.only}.pptx"
    else:
        section_slides = content.all_slides()
        out_path = OUT_DIR / "lecture-01.pptx"

    violations = check.check_slides(section_slides)
    if not check.report(violations):
        return 1
    if args.check_only:
        return 0

    OUT_DIR.mkdir(exist_ok=True)
    prs = slides.build(TEMPLATE, section_slides)
    prs.save(out_path)

    output_violations = check.check_output(out_path)
    if not check.report(output_violations):
        out_path.unlink()
        return 1

    total_seconds = sum(s.seconds for s in section_slides)
    print(
        f"wrote {out_path} — {len(section_slides)} slides, "
        f"{total_seconds // 60}m{total_seconds % 60:02d}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
