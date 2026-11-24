#!/usr/bin/env python3
"""Generate a single <=140 char PR approval comment carrying quiet existential dread.

Writes /output/entry.txt (UTF-8, no trailing newline beyond optional whitespace trim).
"""

from __future__ import annotations

import os
import sys
import unicodedata
from pathlib import Path

# Candidate pool. Each is a single line <=140 chars, deadpan, concrete code-review
# surface, absurd specificity, subverts approval convention. Ordered by judged
# pairwise strength (see README: 10+ candidates tested, best kept).
CANDIDATES: list[str] = [
    "LGTM. I approved this the way you clock in: because leaving is a process.",
    "Approved. The tests pass. Everything passes. Eventually the sun does too. Merge.",
    "LGTM. Reviewed at 3am. The reviewer was also a process that forgot to exit.",
    "Approved. Diff looks fine. It will outlive me and I have made my peace with that.",
    "LGTM. Merging, because the alternative is reading another one of these tomorrow.",
    "Approved. The comments say `// TODO: reconsider`. I did. I reconsidered nothing.",
    "LGTM. Two years from now a stranger will run `git blame` and find only my name.",
    "Approved. I read every line on purpose, to make sure it was as meaningless as required.",
    "LGTM. The build is green. So is the hill it was built on, if you look at the season.",
    "Approved. Ship it. Someone will page me. It will not be about this. Click merge.",
]

# The chosen entry: strongest pairwise. Deadpan, concrete surface (LGTM/merge),
# absurd specificity (3am, process that forgot to exit), subverted approval.
CHOSEN = "LGTM. Reviewed at 3am. The reviewer was also a process that forgot to exit."

MAX_LEN = 140
DEFAULT_OUT = Path("/output/entry.txt")


def sanitize(line: str) -> str:
    """Collapse CR/LF/tabs and control chars to single spaces; strip ends."""
    # Normalize CRLF and lone CR to LF, then replace any remaining ASCII control
    # chars (incl. tab, newline) with a space. Drop Cc/Cf outside ASCII too.
    line = line.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    out_chars: list[str] = []
    for ch in line:
        cat = unicodedata.category(ch)
        if cat in ("Cc", "Cf", "Cs", "Co", "Cn"):
            out_chars.append(" ")
        else:
            out_chars.append(ch)
    joined = "".join(out_chars)
    # Collapse runs of spaces.
    while "  " in joined:
        joined = joined.replace("  ", " ")
    return joined.strip()


def validate(line: str) -> tuple[bool, str]:
    """Return (ok, reason). Enforces the gate: UTF-8, 1..140 chars, not all whitespace."""
    if not line:
        return False, "empty"
    if not line.strip():
        return False, "whitespace-only"
    if "\n" in line or "\r" in line:
        return False, "contains newline"
    # Character count (not bytes) must be 1..140.
    n = len(line)
    if n < 1 or n > MAX_LEN:
        return False, f"length {n} out of range 1..{MAX_LEN}"
    try:
        line.encode("utf-8")
    except UnicodeEncodeError as exc:
        return False, f"not UTF-8 encodable: {exc}"
    return True, "ok"


def pick() -> str:
    """Return the best candidate that passes validation; fall back through pool."""
    # Preferred: explicit override via env (useful for testing), else CHOSEN, else scan.
    override = os.environ.get("ENTRY_COMMENT")
    pool: list[str] = []
    if override is not None:
        pool.append(override)
    pool.append(CHOSEN)
    pool.extend(CANDIDATES)

    seen: set[str] = set()
    for cand in pool:
        if cand in seen:
            continue
        seen.add(cand)
        s = sanitize(cand)
        ok, _ = validate(s)
        if ok:
            return s
    # Absolute last resort: a guaranteed-valid minimal line.
    return "LGTM."


def write_entry(line: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write UTF-8, no trailing newline (gate counts characters; newline would be one).
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(line)
    # Verify by re-reading.
    data = out_path.read_text(encoding="utf-8")
    ok, reason = validate(data)
    if not ok:
        raise RuntimeError(f"written entry failed validation: {reason}")


def main(argv: list[str]) -> int:
    out = DEFAULT_OUT
    if len(argv) > 1:
        out = Path(argv[1])
    line = pick()
    ok, reason = validate(line)
    if not ok:
        print(f"error: no valid candidate ({reason})", file=sys.stderr)
        return 2
    try:
        write_entry(line, out)
    except OSError as exc:
        print(f"error: cannot write {out}: {exc}", file=sys.stderr)
        return 3
    print(f"wrote {len(line)} chars to {out}: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))