
.PHONY: all pc gs clean

all: pc

# Build all module PDFs first (required for \includepdf)
gs: G1S.pdf G2S.pdf G3S.pdf G4S.pdf G5S.pdf

G1S.pdf: G1S.tex V_macros.tex ; latexmk -pdf -interaction=nonstopmode -file-line-error G1S.tex
G2S.pdf: G2S.tex V_macros.tex ; latexmk -pdf -interaction=nonstopmode -file-line-error G2S.tex
G3S.pdf: G3S.tex V_macros.tex ; latexmk -pdf -interaction=nonstopmode -file-line-error G3S.tex
G4S.pdf: G4S.tex V_macros.tex ; latexmk -pdf -interaction=nonstopmode -file-line-error G4S.tex
G5S.pdf: G5S.tex V_macros.tex ; latexmk -pdf -interaction=nonstopmode -file-line-error G5S.tex

# Master: depends on compiled module PDFs for inclusion
pc: gs P_clean.pdf

P_clean.pdf: P_clean.tex V_macros.tex G1S.pdf G2S.pdf G3S.pdf G4S.pdf G5S.pdf
	latexmk -pdf -interaction=nonstopmode -file-line-error P_clean.tex

clean:
	latexmk -C
	rm -f G1S.pdf G2S.pdf G3S.pdf G4S.pdf G5S.pdf

