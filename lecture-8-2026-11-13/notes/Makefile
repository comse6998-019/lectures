# Makefile: run `make` or `make clean` from notes/, or `make -C notes` from the lecture folder.
SHELL := /bin/bash
NOTES_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
DOC := lecture-7

.PHONY: all clean

# Build the lecture notes and fail on unresolved references or missing characters.
all:
	@set -euo pipefail; \
	cd "$(NOTES_DIR)"; \
	tectonic --keep-logs --keep-intermediates $(DOC).tex; \
	if grep -qE "Reference .* undefined|There were undefined|Missing character" $(DOC).log; then \
	  echo "BUILD FAILED: undefined references or missing characters"; \
	  grep -E "undefined|Missing character" $(DOC).log; \
	  exit 1; \
	fi; \
	echo "pages: $$(pdfinfo $(DOC).pdf | awk '/^Pages/{print $$2}')"

# Remove compilation intermediates, keeping the generated PDF.
clean:
	@cd "$(NOTES_DIR)" && rm -f $(DOC).{aux,log,out,toc,lof,lot,xdv,synctex.gz,fls,fdb_latexmk}
