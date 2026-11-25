#!/usr/bin/env python3
"""The Battery's Last Text to Its Charger — make.fun entry.

Writes the winning one-line text from the phone battery to its charger
to /output/entry.txt. The line is a single line, 141 characters
(limit 200), chosen by a local pairwise tournament judged against the
bounty's published judge brief (see README.md for the tournament table).
"""

import os

# Winning line (tournament winner — see README.md).
# Local tournament: 14 candidates, Swiss 3 rounds (21 games) + final,
# 44 judge calls on the Caffeine Inference router, every game played
# in both label orders. #2 led the Swiss at 2.10, #3 second at 1.80;
# the final went to #2, 0.8-0.2.
# validate() below checks the full sealed-scorer gate from the kit's
# competition.yaml verbatim — UTF-8 text, 1-200 characters, not only
# whitespace, a single line (no \n or \r) — so a bad line fails loudly
# here instead of scoring Valid 0 at grading.
ENTRY = (
    "i waited all day by the outlet like a dog at the door. "
    "you walked past me 14 times. 14. i'm at 2% and i've decided: "
    "i'm haunting the charger."
)


def output_dir() -> str:
    """Grader output dir: MAKEFUN_OUTPUT_DIR when set, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def validate(line: str) -> str:
    """Check `line` against the kit's sealed-scorer gate, verbatim.

    competition.yaml: "/output/entry.txt is UTF-8 text of 1 to 200
    characters, not only white space". Single-line follows from the
    task itself (one line, at most 200 characters). Returns the line
    unchanged; raises AssertionError on any gate violation.
    """
    assert isinstance(line, str), "entry must be text"
    # UTF-8: encoding round-trips only if the text is encodable.
    line.encode("utf-8")
    assert 1 <= len(line) <= 200, (
        f"entry must be 1-200 characters, got {len(line)}"
    )
    assert line.strip(), "entry must not be only whitespace"
    assert "\n" not in line and "\r" not in line, (
        "entry must be a single line"
    )
    return line


def write_entry(line: str, outdir: str) -> str:
    """Write `line` to entry.txt atomically, then flush to disk.

    Writes to a temp file in the same directory, flushes and fsyncs
    it so the bytes are durable, then atomically renames it over
    entry.txt and fsyncs the directory. Replaces the old direct
    open/write, which could leave a torn file if the run was killed
    mid-write. Returns the final path.
    """
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.txt")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dir_fd = os.open(outdir, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
    return path


def verify_written(path: str, expected: str) -> None:
    """Read-back gate: entry.txt on disk must equal `expected` exactly.

    Reads the file back as bytes and compares byte-for-byte against
    the UTF-8 encoding of the expected line. Raises RuntimeError on
    any mismatch (wrong size or content) instead of silently shipping
    a truncated or corrupted entry to the grader.
    """
    with open(path, "rb") as f:
        actual = f.read()
    wanted = expected.encode("utf-8")
    if actual != wanted:
        raise RuntimeError(
            f"verification failed: {path} is {len(actual)} bytes, "
            f"expected {len(wanted)} bytes"
        )


def main() -> None:
    line = validate(ENTRY.strip())
    path = write_entry(line, output_dir())
    verify_written(path, line)
    print(f"Wrote {len(line)} chars to {path}")
    print(line)


if __name__ == "__main__":
    main()
