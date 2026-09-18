#!/usr/bin/env python3
"""Warn about register slips in the lecture notes. Never fails the build."""
import re, sys

BANNED = ["delve", "leverage", "robust", "comprehensive", "crucial", "landscape",
          "ecosystem", "navigate", "foster", "underscore", "pivotal", "nuanced",
          "holistic", "paramount", "utilize", "utilise", "facilitate", "rung", "ladder",
          "it is worth noting", "it is important to note", "in order to", "prior to"]

def main(path):
    src = open(path, encoding="utf8").read()
    src = src.split(r"\begin{document}", 1)[-1]   # lint the body only
    src = re.sub(r"(?<!\\)%.*", "", src)
    for env in ("lstlisting", "verbatim", "tikzpicture", "thebibliography", "table", "figure", "tabularx", "tabular"):
        src = re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), "", src, flags=re.S)
    warnings = 0
    lines = src.split("\n")
    for i, line in enumerate(lines, 1):
        line = re.sub(r"``.*?''", "", line)   # verbatim quotations are the source's words, not ours
        if "\u2014" in line or "---" in line:
            print(f"{path}:{i}: em-dash"); warnings += 1
        if re.search(r"\bshould\b", line):
            print(f"{path}:{i}: 'should'"); warnings += 1
        low = line.lower()
        for w in BANNED:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                print(f"{path}:{i}: banned word '{w}'"); warnings += 1
    # long sentences, measured on de-commanded prose
    src = re.sub(r"``.*?''", " Q. ", src, flags=re.S)   # quotations are exempt here too; each ends a sentence
    prose = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", src)
    prose = re.sub(r"[{}&]", " ", prose)
    for m in re.finditer(r"[^.!?]*[.!?]", prose):
        s = m.group(0)
        n = len(s.split())
        if n > 45:
            print(f"{path}: long sentence ({n} words): {s.strip()[:80]}..."); warnings += 1
    print(f"lint: {warnings} warning(s)")

if __name__ == "__main__":
    main(sys.argv[1])
