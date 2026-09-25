# Makefile: run `make -f build.sh` or `make -f build.sh clean`.
SHELL := /bin/bash
NOTES_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: all clean

# Build the lecture notes and fail on unresolved references.
all:
	@set -euo pipefail; \
	cd "$(NOTES_DIR)"; \
	tectonic --keep-logs --keep-intermediates lecture_notes.tex; \
	if grep -qE "Citation .* undefined|Reference .* undefined|There were undefined" lecture_notes.log; then \
	  echo "BUILD FAILED: undefined references or citations"; \
	  grep -E "undefined" lecture_notes.log; \
	  exit 1; \
	fi; \
	echo "pages: $$(pdfinfo lecture_notes.pdf | awk '/^Pages/{print $$2}')"; \
	echo "demo stubs: $$(cat sections/*.tex | grep -c 'begin{demostub}' || true)"; \
	echo "figure callouts: $$(cat sections/*.tex | grep -c 'begin{figneeded}' || true)"; \
	for f in sections/*.tex; do python3 lint.py "$$f" | grep -v '^lint:' || true; done

# Remove compilation intermediates, keeping the generated PDF.
clean:
	@cd "$(NOTES_DIR)" && \
	rm -f lecture_notes.{aux,log,out,toc,lof,lot,bbl,blg,bcf,run.xml,xdv,synctex.gz,fls,fdb_latexmk}
