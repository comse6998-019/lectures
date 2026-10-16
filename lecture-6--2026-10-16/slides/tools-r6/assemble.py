"""Assemble the reading PDF: chosen pages of the full PowerPoint export, every annotation removed, each page labelled with its deck slide number.
usage: python3 assemble.py <full.pdf> <keep.json> <out.pdf>"""
import sys, json
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, ArrayObject, DictionaryObject, TextStringObject
src, keep, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
r = PdfReader(src); w = PdfWriter()
for n in keep:
    page = w.add_page(r.pages[n - 1])
    for key in ("/Annots", "/AA"):
        if key in page: del page[key]
nums = ArrayObject()
for i, n in enumerate(keep):
    nums += [NumberObject(i), DictionaryObject({NameObject("/S"): NameObject("/D"), NameObject("/St"): NumberObject(n)})]
w._root_object[NameObject("/PageLabels")] = DictionaryObject({NameObject("/Nums"): nums})
w.add_metadata({"/Title": "Designing Production Agentic Systems, Lecture 6"})
w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
with open(out, "wb") as f: w.write(f)
print("wrote", out, len(keep), "pages")
