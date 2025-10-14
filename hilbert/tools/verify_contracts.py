#!/usr/bin/env python3
# Contract Compliance Engine for V-layer LaTeX projects
# Rules: V1–V6 (see print_rulebook())
# Usage: python3 tools/verify_contracts.py
import re, sys, json
from pathlib import Path

# --------- CONFIG (adjust if your file names differ) ----------
FILES = {
    "G2S": Path("G2S.tex"),
    "G3S": Path("G3S.tex"),
    "G4S": Path("G4S.tex"),
    "G1S": Path("G1S.tex"),
    "G5S": Path("G5S.tex"),
    "PCLEAN": Path("P_clean.tex"),
    # add "G6S": Path("G6S.tex") if using Cook–Levin module
}
V_MACROS = Path("V_macros.tex")

# Distance window (characters) for “nearby” checks
NEAR_WINDOW = 400

# ----------------------------------------------------------------
def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return ""

def find_near(text, token_a, token_b, window=NEAR_WINDOW):
    """Return True if token_b appears within +-window chars of any token_a match."""
    out = []
    for m in re.finditer(re.escape(token_a), text):
        aidx = m.start()
        lo, hi = max(0, aidx - window), aidx + window
        if re.search(re.escape(token_b), text[lo:hi]):
            out.append((aidx, token_a, token_b))
    return bool(out)

def count_tokens(text, pattern):
    return len(re.findall(pattern, text))

def has_token(text, token):
    return re.search(re.escape(token), text) is not None

def unpaired_left_right(text):
    """Return imbalance of \left ... \right usage (count difference)."""
    left = len(re.findall(r'\\left\b', text))
    right = len(re.findall(r'\\right\b', text))
    return left - right

def lines_with_texorpdfstring(text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if r'\texorpdfstring' in line:
            out.append((i, line.strip()))
    return out

def find_defined_but_unused(text, names):
    """Return list of names defined with \providecommand or \newcommand and never used later."""
    unused = []
    for name in names:
        # detect definition
        def_pat = r'\\(?:providecommand|newcommand)\s*\{\\' + re.escape(name[1:]) + r'\}'
        if re.search(def_pat, text):
            # used at least twice overall? (def + usage) — safer: check usage outside the definition
            # search any occurrence after first definition end
            if len(re.findall(r'\\' + re.escape(name[1:]) + r'\b', text)) <= 1:
                unused.append(name)
    return unused

def print_rulebook():
    print("Rulebook:")
    print(" V1 Strong/Weak Equivalence (G2S): \\StrongForm appears near \\WeakForm.")
    print(" V2 Noether Bridge (G4S + P_clean): G4S uses \\NoetherTensor{...} and P_clean references \\ConcludeDivT.")
    print(" V3 Coercivity Interpretation (G2S): \\InterpCoercivityToStability is near coercivity/\\Bform discussion.")
    print(" V4 Discrete Convergence (G3S): both \\DeltaFourh and \\InterpDiscToContStability appear.")
    print(" V5 Title Safety (all): files with \\texorpdfstring must not have unbalanced \\left/\\right.")
    print(" V6 Unused Macro Detection (module-local): report local helpers defined but never used.\n")

def main():
    print_rulebook()
    results = []
    summary = {"pass": 0, "fail": 0, "warn": 0}

    # --------- Load texts ----------
    texts = {k: read(v) for k, v in FILES.items()}
    if not any(texts.values()):
        print("ERROR: Could not read any .tex files. Are paths ok?")
        sys.exit(2)

    # ---------- V1 ----------
    g2 = texts.get("G2S", "")
    v1_ok = has_token(g2, r'\StrongForm') and has_token(g2, r'\WeakForm') \
            and find_near(g2, r'\StrongForm', r'\WeakForm')
    results.append(("V1", v1_ok, "G2S must show \\StrongForm near \\WeakForm."))

    # ---------- V2 ----------
    g4 = texts.get("G4S", "")
    pclean = texts.get("PCLEAN", "")
    v2_ok = has_token(g4, r'\NoetherTensor') and has_token(pclean, r'\ConcludeDivT')
    results.append(("V2", v2_ok, "G4S must use \\NoetherTensor, P_clean must reference \\ConcludeDivT."))

    # ---------- V3 ----------
    v3_ok = has_token(g2, r'\InterpCoercivityToStability') and \
            (has_token(g2, r'coerciv') or has_token(g2, r'\\Bform'))
    # optional “nearby” tightening:
    v3_ok = v3_ok and find_near(g2, r'\InterpCoercivityToStability', r'coerciv|\\Bform')
    results.append(("V3", v3_ok, "G2S must pair \\InterpCoercivityToStability with coercivity/\\Bform discussion."))

    # ---------- V4 ----------
    g3 = texts.get("G3S", "")
    v4_ok = has_token(g3, r'\DeltaFourh') and has_token(g3, r'\InterpDiscToContStability')
    results.append(("V4", v4_ok, "G3S must include \\DeltaFourh and \\InterpDiscToContStability."))

    # ---------- V5 ----------
    # For each file: if it uses \texorpdfstring, ensure \left and \right are balanced
    v5_all_ok = True
    v5_details = []
    for name, txt in texts.items():
        if not txt:
            continue
        if lines_with_texorpdfstring(txt):
            balance = unpaired_left_right(txt)
            if balance != 0:
                v5_all_ok = False
                v5_details.append(f"{name}: \\left/\\right imbalance = {balance}")
    v5_msg = "All files using \\texorpdfstring have balanced \\left/\\right." + \
             ("" if not v5_details else " Imbalances: " + "; ".join(v5_details))
    results.append(("V5", v5_all_ok, v5_msg))

    # ---------- V6 ----------
    # Quick heuristic: common locals that sometimes get defined and forgotten
    suspects = [r'\Rfunc', r'\Jfunc', r'\Acal', r'\Hspace', r'\Domain',
                r'\DeltaTwoh', r'\DeltaFourh', r'\Bformh', r'\Sh', r'\Xi']
    v6_ok = True
    v6_notes = []
    for mod in ("G1S", "G2S", "G3S", "G4S", "G5S"):
        t = texts.get(mod, "")
        if not t:
            continue
        unused = find_defined_but_unused(t, suspects)
        if unused:
            v6_ok = False
            v6_notes.append(f"{mod}: defined but unused -> {', '.join(unused)}")
    v6_msg = "No unused locally-defined helpers." + ("" if not v6_notes else " " + " | ".join(v6_notes))
    results.append(("V6", v6_ok, v6_msg))

    # ---------- Report ----------
    print("\n=== Contract Compliance Report ===")
    for rule, ok, msg in results:
        if ok:
            print(f"[PASS] {rule}: {msg}")
            summary["pass"] += 1
        else:
            print(f"[FAIL] {rule}: {msg}")
            summary["fail"] += 1

    # Pretty exit code policy: fail if any hard rule fails (V1–V4). V5, V6 can be treated as warnings if you prefer.
    hard_fail = any((r[0] in ("V1","V2","V3","V4")) and (not r[1]) for r in results)
    if hard_fail:
        print("\nResult: HARD FAIL (fix V1–V4).")
        sys.exit(1)
    elif not results or any(not r[1] for r in results):
        print("\nResult: SOFT WARN (some non-hard checks failed).")
        sys.exit(0)
    else:
        print("\nResult: ALL GREEN.")
        sys.exit(0)

if __name__ == "__main__":
    main()

