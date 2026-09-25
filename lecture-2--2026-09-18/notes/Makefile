# Makefile: run `make` or `make clean` from notes/, or `make -C notes` from the lecture folder.
SHELL := /bin/bash
NOTES_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
DOC := lecture-2

.PHONY: all clean

# Build the lecture notes and fail on unresolved references.
all:
	@set -euo pipefail; \
	cd "$(NOTES_DIR)"; \
	tectonic --keep-logs --keep-intermediates --synctex $(DOC).tex; \
	if grep -qE "Citation .* undefined|Reference .* undefined|There were undefined" $(DOC).log; then \
	  echo "BUILD FAILED: undefined references or citations"; \
	  grep -E "undefined" $(DOC).log; \
	  exit 1; \
	fi; \
	echo "pages: $$(pdfinfo $(DOC).pdf | awk '/^Pages/{print $$2}')"; \
	echo "demo stubs: $$(cat sections/*.tex | grep -c 'begin{demostub}' || true)"; \
	echo "figure callouts: $$(cat sections/*.tex | grep -c 'begin{figneeded}' || true)"; \
	if [ -f lint.py ]; then \
	  for f in sections/*.tex; do python3 lint.py "$$f" | grep -v '^lint:' || true; done; \
	else \
	  echo "lint: lint.py not found; per-section lint skipped"; \
	fi

# Remove compilation intermediates, keeping the generated PDF.
clean:
	@cd "$(NOTES_DIR)" && \
	rm -f $(DOC).{aux,log,out,toc,lof,lot,bbl,blg,bcf,run.xml,xdv,synctex.gz,fls,fdb_latexmk}
