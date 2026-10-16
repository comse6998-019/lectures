#!/usr/bin/env python3
"""Compile TikZ sources to PDF and SVG. Requires tectonic and pdftocairo."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
build=ROOT/'build';build.mkdir(exist_ok=True)
names=sys.argv[1:] or [p.stem for p in sorted(ROOT.glob('*.tikz'))]
for name in names:
 if not (ROOT/(name+'.tikz')).is_file() or Path(name).name!=name:
  raise SystemExit('Unknown figure: '+name)
 wrapper=ROOT/(name+'.tex')
 wrapper.write_text('\\input{standalone-style.tex}\n\\begin{document}\n\\input{'+name+'.tikz}\n\\end{document}\n')
 result=subprocess.run(['tectonic','--keep-logs','--outdir',str(build),str(wrapper)],cwd=ROOT,capture_output=True,text=True)
 (build/(name+'.build.txt')).write_text(result.stdout+result.stderr)
 if result.returncode:raise SystemExit(name+': '+result.stdout+result.stderr)
 subprocess.run(['pdftocairo','-svg',str(build/(name+'.pdf')),str(ROOT/(name+'.svg'))],check=True)
 print(name+': rendered',flush=True)
