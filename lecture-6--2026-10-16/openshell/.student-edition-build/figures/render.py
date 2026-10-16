"""Compile the student edition's TikZ figures to SVG.

Each NAME.tikz here is wrapped with the guide's own style file
(../../openshell-figures/standalone-style.tex), compiled with tectonic in a
temporary folder, and converted with pdftocairo; only NAME.svg is written
beside the source, so the folder holds sources and SVGs and nothing else.

Run from anywhere:
  uv run --no-project --python 3.12 python render.py            # every figure
  uv run --no-project --python 3.12 python render.py three-needs
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
STYLE = HERE.parent.parent / 'openshell-figures' / 'standalone-style.tex'

names = sys.argv[1:] or [p.stem for p in sorted(HERE.glob('*.tikz'))]
for name in names:
    source = HERE / (name + '.tikz')
    if Path(name).name != name or not source.is_file():
        raise SystemExit('Unknown figure: ' + name)
    with tempfile.TemporaryDirectory() as tmp:
        build = Path(tmp)
        shutil.copy(STYLE, build / 'standalone-style.tex')
        shutil.copy(source, build / source.name)
        wrapper = build / (name + '.tex')
        wrapper.write_text('\\input{standalone-style.tex}\n\\begin{document}\n\\input{'
                           + name + '.tikz}\n\\end{document}\n')
        result = subprocess.run(['tectonic', '--keep-logs', str(wrapper)], cwd=build,
                                capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(name + ': ' + result.stdout + result.stderr)
        overfull = [line for line in (build / (name + '.log')).read_text(errors='replace').splitlines()
                    if line.startswith(('Overfull', 'Underfull'))]
        if overfull:
            print(name + ': ' + '; '.join(overfull), flush=True)
        subprocess.run(['pdftocairo', '-svg', str(build / (name + '.pdf')), str(HERE / (name + '.svg'))],
                       check=True)
        # A PNG proof for looking at the figure lands in the folder named by
        # STUDENT_EDITION_PROOFS (a scratch folder), never beside the source.
        proofs = os.environ.get('STUDENT_EDITION_PROOFS')
        if proofs:
            Path(proofs).mkdir(parents=True, exist_ok=True)
            subprocess.run(['pdftocairo', '-png', '-r', '200', '-singlefile', str(build / (name + '.pdf')),
                            str(Path(proofs) / name)], check=True)
    print(name + ': rendered', flush=True)
