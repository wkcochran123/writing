# ================================================================
# Makefile for the monograph build
# Requires: latexmk (recommended), pdflatex (or lualatex/xelatex), biber/bibtex if you have a .bib
# ================================================================

# You can switch engine by setting LATEXMK_ENGINE= -pdf, -pdflua, or -pdfxe
LATEXMK_ENGINE ?= -pdf
LATEXMK_FLAGS  ?= -halt-on-error -interaction=nonstopmode -file-line-error

TEXFILES = P_clean.tex P.tex G1S.tex G2S.tex G3S.tex V_article.tex
AUX_CLEAN = *.aux *.bbl *.bcf *.blg *.fdb_latexmk *.fls *.log *.out *.run.xml *.toc *.synctex.gz

all: pclean p g1s g2s g3s v

v: V_article.pdf

pclean: P_clean.pdf

p: P.pdf

g1s: G1S.pdf

g2s: G2S.pdf

g3s: G3S.pdf

# Generic build rules
%.pdf: %.tex V_macros.tex
	latexmk $(LATEXMK_ENGINE) $(LATEXMK_FLAGS) $<

# Phony helpers
.PHONY: clean distclean watch help

watch:
	latexmk $(LATEXMK_ENGINE) $(LATEXMK_FLAGS) -pvc V_article.tex

clean:
	latexmk -C
	rm -f $(AUX_CLEAN)

distclean: clean
	rm -f *.pdf

help:
	@echo "Targets:"
	@echo "  make all      -> build P_clean, P, G1S, G2S, G3S, and V_article"
	@echo "  make v        -> build V_article.pdf (human-readable Rosetta guide)"
	@echo "  make pclean   -> build P_clean.pdf"
	@echo "  make p        -> build P.pdf"
	@echo "  make g1s      -> build G1S.pdf"
	@echo "  make g2s      -> build G2S.pdf"
	@echo "  make g3s      -> build G3S.pdf"
	@echo "  make watch    -> live preview V_article.tex with latexmk -pvc"
	@echo "  make clean    -> remove aux files"
	@echo "  make distclean-> remove aux + pdfs"
