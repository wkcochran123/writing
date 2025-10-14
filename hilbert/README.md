# Build Utilities and Rosetta Layer

This bundle gives you **full building utilities** and a clean split between the
guarded macro layer and the human-readable article.

## Files

- `V_macros.tex` — the **pure Rosetta layer** (no packages, no envs). Safe to `\input` anywhere.
- `V_article.tex` — a **standalone article** that includes `V_macros.tex` and explains the contracts.
- `V_standalone.tex` — tiny wrapper; also builds the article.
- `Makefile` — convenient targets to build everything with `latexmk`.
- `latexmkrc` — minimal configuration for latexmk.

Your existing files (`P_clean.tex`, `P.tex`, `G1S.tex`, `G2S.tex`, `G3S.tex`) are assumed to
be in the same directory. They will build if they already compile alone; otherwise,
update them to `\input{V_macros.tex}` near the top to unify notation.

## Quick Start

```bash
# Build the human-readable V article
make v

# Build everything (including P_clean, P, G1S, G2S, G3S)
make all

# Live preview (auto-rebuild V_article on change)
make watch

# Clean aux files
make clean

# Nuclear clean (aux + PDFs)
make distclean
```

## Integrating the Rosetta Layer

In each chapter or module that uses the shared notation, add near the top:
```tex
\input{V_macros.tex}
```
This introduces only **guarded** macros and will not conflict with your packages
or theorem environments.

If you currently have a `V.tex` in your tree, you can either replace its
contents with `V_macros.tex` or keep both (use `V_article.tex` for the PDF guide,
`V_macros.tex` for the shim used by the other files).

---

If you want me to also emit a `ci.yml` for GitHub Actions or a `justfile`/`ninja`
setup, say the word and I’ll drop those in too.
