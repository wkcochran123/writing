# ============================
# Causal Closure Build System
# Flat / Non-Recursive Makefile
# ============================

# -------- User knobs (safe defaults) -------------------------------
# Auto-detect \includepdf usage in P_clean/V_article (1 if present, else 0)
DETECT_PDFS := $(shell grep -E '\\\\includepdf\\b' -q P_clean.tex V_article.tex 2>/dev/null && echo 1 || echo 0)
USE_PDFS ?= $(DETECT_PDFS)

# Master docs
MASTER       := P_clean
AUX_ARTICLE  := V_article

# Modules
MODULES      := G1S G2S G3S G4S G5S
MODULE_TEX   := $(MODULES:=.tex)
MODULE_PDF   := $(MODULES:=.pdf)

# Common deps
COMMON_DEPS  := V_macros.tex

# Tools (preview explicitly disabled)
PDFLATEX     := pdflatex -interaction=nonstopmode -file-line-error
LATEXMK_BIN  := $(shell command -v latexmk >/dev/null 2>&1 && echo yes || echo no)
LATEXMK      := latexmk -pdf -pv- -pvc- -interaction=nonstopmode -file-line-error

# Bundle sources (and optionally module PDFs)
SRC_BUNDLE   := $(COMMON_DEPS) $(MASTER).tex $(AUX_ARTICLE).tex $(MODULE_TEX)
ifeq ($(USE_PDFS),1)
  BUNDLE_FILES := $(SRC_BUNDLE) $(MODULE_PDF)
else
  BUNDLE_FILES := $(SRC_BUNDLE)
endif

# Phony
.PHONY: all pdf article modules fast draft watch lint verify verify-nontail clean realclean bundle arxiv help status

# -------------------------------------------------------------------
all: pdf

# ----- Master build -------------------------------------------------
ifeq ($(USE_PDFS),1)
$(MASTER).pdf: $(MASTER).tex $(COMMON_DEPS) $(MODULE_PDF)
	@echo "==> Building $@ [PDF-inclusion mode]"
	@if [ "$(LATEXMK_BIN)" = "yes" ]; then \
		$(LATEXMK) $(MASTER).tex; \
	else \
		$(PDFLATEX) $(MASTER).tex; \
		$(PDFLATEX) $(MASTER).tex; \
	fi
else
$(MASTER).pdf: $(MASTER).tex $(COMMON_DEPS) $(MODULE_TEX)
	@echo "==> Building $@ [source-inclusion mode]"
	@if [ "$(LATEXMK_BIN)" = "yes" ]; then \
		$(LATEXMK) $(MASTER).tex; \
	else \
		$(PDFLATEX) $(MASTER).tex; \
		$(PDFLATEX) $(MASTER).tex; \
	fi
endif

pdf: $(MASTER).pdf

# ----- Article build ------------------------------------------------
ifeq ($(USE_PDFS),1)
$(AUX_ARTICLE).pdf: $(AUX_ARTICLE).tex $(COMMON_DEPS) $(MODULE_PDF)
	@echo "==> Building $@ [PDF-inclusion mode]"
	@if [ "$(LATEXMK_BIN)" = "yes" ]; then \
		$(LATEXMK) $(AUX_ARTICLE).tex; \
	else \
		$(PDFLATEX) $(AUX_ARTICLE).tex; \
		$(PDFLATEX) $(AUX_ARTICLE).tex; \
	fi
else
$(AUX_ARTICLE).pdf: $(AUX_ARTICLE).tex $(COMMON_DEPS) $(MODULE_TEX)
	@echo "==> Building $@ [source-inclusion mode]"
	@if [ "$(LATEXMK_BIN)" = "yes" ]; then \
		$(LATEXMK) $(AUX_ARTICLE).tex; \
	else \
		$(PDFLATEX) $(AUX_ARTICLE).tex; \
		$(PDFLATEX) $(AUX_ARTICLE).tex; \
	fi
endif

article: $(AUX_ARTICLE).pdf

# ----- Module builds -----------------------------------------------
%.pdf: %.tex $(COMMON_DEPS)
	@echo "==> Building module $@"
	@if [ "$(LATEXMK_BIN)" = "yes" ]; then \
		$(LATEXMK) $<; \
	else \
		$(PDFLATEX) $<; \
		$(PDFLATEX) $<; \
	fi

modules: $(MODULE_PDF)

# ----- Fast & draft -------------------------------------------------
fast:
	@echo "==> FAST build (single pass) $(MASTER).tex"
	$(PDFLATEX) $(MASTER).tex

draft:
	@echo "==> DRAFT build $(MASTER).tex"
	@if [ "$(LATEXMK_BIN)" = "yes" ]; then \
		$(LATEXMK) -pdf -pv- -pvc- -pdflatex='$(PDFLATEX) -draftmode' $(MASTER).tex; \
	else \
		$(PDFLATEX) -draftmode $(MASTER).tex; \
	fi

# ----- Watch (explicit; still no auto preview) ---------------------
watch:
	@echo "==> WATCH mode (latexmk -pvc; preview disabled)"
	@if [ "$(LATEXMK_BIN)" = "yes" ]; then \
		$(LATEXMK) -pdf -pvc -pv- $(MASTER).tex; \
	else \
		echo "latexmk not found; watch mode unavailable."; \
		exit 1; \
	fi

# ----- Lint (V-layer discipline) -----------------------------------
lint:
	@echo "==> LINT: V-layer checks"
	@# 0) Basic existence
	@if [ ! -f "$(COMMON_DEPS)" ]; then echo "[FAIL] Missing $(COMMON_DEPS)"; exit 2; fi
	@if [ ! -f "$(MASTER).tex" ]; then echo "[FAIL] Missing $(MASTER).tex"; exit 2; fi
	@# 1) Unpaired \left/\right (simple heuristic)
	@if grep -R --include='*.tex' -n '\\left[^ ]*$$' . >/dev/null; then echo '[FAIL] Unpaired \\left (line ends after \\left)'; exit 2; fi || true
	@if grep -R --include='*.tex' -n '\\right[^ ]*$$' . >/dev/null; then echo '[FAIL] Unpaired \\right (line ends after \\right)'; exit 2; fi || true
	@# 2) Titles: math in title should be texorpdfstring (warn)
	@if grep -nE '\\\\title\\{.*\\$' $(MASTER).tex $(AUX_ARTICLE).tex 2>/dev/null; then echo '[WARN] Math in title: ensure \\texorpdfstring'; fi || true
	@# 3) Core handles presence (hint)
	@if ! grep -R --include='*.tex' '\\StrongForm\\|\\WeakForm\\|\\ConcludeDivT\\|\\GOneStatement' . >/dev/null; then \
		echo '[WARN] Core handles not spotted in sources.'; fi
	@echo "[OK] Lint complete."

# ----- Verify (semantic-ish checks) --------------------------------
verify: lint verify-nontail
	@echo "[OK] verify complete."

# Tail-recursive discipline: ensure modules don’t input each other’s sources
verify-nontail:
	@echo "==> Checking tail-recursive discipline"
	@if grep -R --include='G*S.tex' -nE '\\input\\{G[1-9]S\\.tex\\}' . >/dev/null; then \
	  echo '[FAIL] Non-tail coupling: a G*S.tex inputs another G*S.tex'; exit 2; \
	else echo '[OK] Tail recursion preserved'; fi

# ----- Clean --------------------------------------------------------
clean:
	@echo "==> Cleaning aux files"
	@rm -f *.aux *.bbl *.bcf *.blg *.fdb_latexmk *.fls *.log *.out *.run.xml *.synctex.gz *.toc *.lof *.lot
	@for f in $(MODULE_TEX) $(MASTER).tex $(AUX_ARTICLE).tex; do \
		if [ -f "$$f" ] && [ "$(LATEXMK_BIN)" = "yes" ]; then $(LATEXMK) -c "$$f" >/dev/null 2>&1; fi; \
	done
	@echo "Cleaned aux files."

realclean: clean
	@echo "==> Removing PDFs"
	@rm -f $(MASTER).pdf $(AUX_ARTICLE).pdf $(MODULE_PDF)
	@echo "Removed aux + PDFs."

# ----- Bundles ------------------------------------------------------
bundle: $(MASTER).pdf
	@echo "==> Creating bundle.zip"
	@zip -q -9 bundle.zip $(BUNDLE_FILES)

arxiv:
	@echo "==> Creating arxiv.zip (sources only)"
	@zip -q -9 arxiv.zip $(SRC_BUNDLE)

# ----- Status/Help --------------------------------------------------
status:
	@echo "Modules discovered: $(if $(MODULE_TEX),$(MODULE_TEX),<none>)"
	@echo "PDFs expected     : $(if $(MODULE_PDF),$(MODULE_PDF),<none>)"
	@echo "Master            : $(MASTER).tex"
	@echo "Article           : $(AUX_ARTICLE).tex"
	@echo "Mode              : $(if $(USE_PDFS),PDF Inclusion (1),Source Inclusion (0))"
	@echo "latexmk present   : $(LATEXMK_BIN)"

help:
	@echo "Targets:"
	@echo "  all / pdf       -> build $(MASTER).pdf (modules first)"
	@echo "  modules         -> build module PDFs ($(MODULES))"
	@echo "  article         -> build $(AUX_ARTICLE).pdf"
	@echo "  fast            -> single-pass build (pdflatex)"
	@echo "  draft           -> draftmode build"
	@echo "  watch           -> continuous build (no auto preview)"
	@echo "  lint            -> V-layer checks"
	@echo "  verify          -> lint + tail-recursion discipline"
	@echo "  bundle          -> zip sources (+module PDFs if included)"
	@echo "  arxiv           -> zip sources only"
	@echo "  clean / realclean"
	@echo "  status          -> show build context"

