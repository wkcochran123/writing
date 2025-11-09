# ====== Makefile — V/P project builder (no preview, no watcher) ======

# Tools & flags
LATEXMK    := latexmk
VIEWMODE   := -view=none            # force: never start a PDF viewer
PDFMODE    := -pdf                  # pdflatex
LATEXFLAGS := -interaction=nonstopmode -halt-on-error -file-line-error
# If your environment injects latexmkrc, we still suppress preview via -view=none

# Files
PCLEAN_TEX := P_clean.tex
VMACROS    := V_macros.tex

# Auto-discover all module .tex files named like G#S.tex (G1S.tex ... G9S.tex)
MODULE_TEX := $(wildcard G*S.tex)
MODULE_PDF := $(MODULE_TEX:.tex=.pdf)

# Default target: build P_clean after modules
.PHONY: all
all: P_clean.pdf

# Explicit convenience target
.PHONY: pdf
pdf: P_clean.pdf

# Build all discovered modules (if any)
.PHONY: modules
modules: $(MODULE_PDF)
	@echo "OK: modules up to date: $(MODULE_PDF)"

# Master PDF depends on its source, macros, and module PDFs (so includepdf works)
P_clean.pdf: $(PCLEAN_TEX) $(VMACROS) $(MODULE_PDF)
	$(LATEXMK) $(VIEWMODE) $(PDFMODE) $(LATEXFLAGS) $(PCLEAN_TEX)

# Generic rule: build any .pdf from .tex (ensures V_macros is considered)
%.pdf: %.tex $(VMACROS)
	$(LATEXMK) $(VIEWMODE) $(PDFMODE) $(LATEXFLAGS) $<

# Static analysis / contract verification
VERIFY := tools/verify_contracts.py
.PHONY: verify
verify:
	@if [ -f "$(VERIFY)" ]; then \
	  echo "Running verifier…"; \
	  python3 "$(VERIFY)"; \
	else \
	  echo "NOTE: $(VERIFY) not found. Create it, then 'make verify'."; \
	fi

# Clean aux (keep PDFs)
.PHONY: clean
clean:
	@$(LATEXMK) -c
	@for f in $(MODULE_TEX) $(PCLEAN_TEX); do \
	  if [ -f "$$f" ]; then $(LATEXMK) -c "$$f" >/dev/null 2>&1; fi; \
	done
	@echo "Cleaned aux files."

# Real clean (remove PDFs too)
.PHONY: realclean
realclean:
	@$(LATEXMK) -C
	@for f in $(MODULE_TEX) $(PCLEAN_TEX); do \
	  if [ -f "$$f" ]; then $(LATEXMK) -C "$$f" >/dev/null 2>&1; fi; \
	done
	@rm -f $(MODULE_PDF) P_clean.pdf
	@echo "Removed aux + PDFs."

# Friendly status
.PHONY: status
status:
	@echo "Modules discovered: $(if $(MODULE_TEX),$(MODULE_TEX),<none>)"
	@echo "PDFs expected     : $(if $(MODULE_PDF),$(MODULE_PDF),<none>)"
	@echo "Master            : $(PCLEAN_TEX)"

# Help
.PHONY: help
help:
	@echo "Targets:"
	@echo "  make            -> build P_clean.pdf (modules first)"
	@echo "  make modules    -> build all G*S module PDFs"
	@echo "  make pdf        -> alias of 'make P_clean.pdf'"
	@echo "  make verify     -> run tools/verify_contracts.py (if present)"
	@echo "  make clean      -> remove aux files"
	@echo "  make realclean  -> remove aux + PDFs"
	@echo "  make status     -> show discovered modules"

