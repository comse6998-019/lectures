"""Interleave the components build (slides 101 to 108) with the lifecycle build (109 to 115) of lecture6.pptx, so each
lifecycle step follows the component that performs it: the gateway (102) and the record it persists (109), the compute
driver (103) and Provisioning (110), the trusted supervisor (105) and its hello, Ready and the other phases (111 to 113),
and Cyberbird in both (107, 114). A pure reorder of sldIdLst: no slide changes, and no link points into or out of the range.

    cd lecture-6--2026-10-16 && IN=lecture6.pptx OUT=<scratch>/lecture6.r6e.pptx \
        uv run --no-project --python 3.12 --with python-pptx python slides/tools-r6/patch-r6e.py
"""
import os
from pptx import Presentation

IN, OUT = os.environ["IN"], os.environ["OUT"]
COMP, LIFE = "Each OpenShell component has its own job.", "A sandbox is a record before a container."
ORDER = [101, 102, 109, 103, 110, 104, 105, 111, 112, 113, 106, 107, 108, 114, 115]

p = Presentation(IN)
title = lambda n: p.slides[n - 1].shapes.title.text_frame.text
assert len(p.slides) == 222
assert all(title(n).startswith(COMP) for n in range(101, 109)), "slides 101 to 108 are not the components build"
assert all(title(n).startswith(LIFE) for n in range(109, 116)), "slides 109 to 115 are not the lifecycle build"
assert not title(100).startswith(COMP) and not title(116).startswith(LIFE)
lst = p.slides._sldIdLst
ids = list(lst)
for el in ids[100:115]:
    lst.remove(el)
anchor = ids[99]
for n in reversed(ORDER):
    anchor.addnext(ids[n - 1])
p.save(OUT)
q = Presentation(OUT)
print("new order:", [(i, q.slides[i - 1].shapes.title.text_frame.text[:10]) for i in range(100, 117)])
