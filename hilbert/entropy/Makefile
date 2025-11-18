
MAIN = hilbert
TEXBIN = /Library/TeX/texbin

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

clean:
	latexmk -C

distclean: clean
	rm -f $(MAIN).pdf

.PHONY: all clean distclean

