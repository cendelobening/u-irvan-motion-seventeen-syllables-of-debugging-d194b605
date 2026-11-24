"""Seventeen Syllables of Debugging entry.

Writes one original haiku about debugging to <output dir>/entry.txt
and verifies the file afterwards. Pure standard library.
"""

import os
import stat
import tempfile

# The one haiku. A cursor blinking at 3am, a log scrolling through the
# night, and the last line turning the whole search back on the debugger:
# the fault was never in the code under watch, it was the watcher.
HAIKU = (
    "cursor blinks at three\n"
    "the log scrolls on through the night\n"
    "the bug was my own"
)

# Syllable count for every word used in the haiku, checked by hand
# against a dictionary count (cursor = cur-sor, scrolls = one).
SYLLABLES = {
    "cursor": 2,
    "blinks": 1,
    "at": 1,
    "three": 1,
    "the": 1,
    "log": 1,
    "scrolls": 1,
    "on": 1,
    "through": 1,
    "night": 1,
    "bug": 1,
    "was": 1,
    "my": 1,
    "own": 1,
}

EXPECTED_COUNTS = (5, 7, 5)
MAX_LENGTH = 200


def count_syllables(line):
    """Count the syllables of one line from the built-in word table."""
    total = 0
    for word in line.split():
        if word not in SYLLABLES:
            raise ValueError("no syllable count for word %r" % word)
        total += SYLLABLES[word]
    return total


def check_haiku(haiku):
    """Make sure the haiku is exactly 3 lines in 5-7-5, within the limit."""
    if not isinstance(haiku, str):
        raise ValueError("haiku must be a string")
    if not haiku.strip():
        raise ValueError("haiku must not be only whitespace")
    if haiku != haiku.strip():
        raise ValueError("haiku must have no leading or trailing whitespace")
    if "\r" in haiku:
        raise ValueError("haiku must not contain carriage returns")
    lines = haiku.split("\n")
    if len(lines) != 3:
        raise ValueError("haiku must be exactly 3 lines, got %d" % len(lines))
    for line, expected in zip(lines, EXPECTED_COUNTS):
        if not line.strip():
            raise ValueError("haiku lines must not be empty")
        if line != line.strip():
            raise ValueError("haiku lines must have no leading or trailing whitespace")
        if "  " in line:
            raise ValueError("haiku lines must not contain double spaces")
        got = count_syllables(line)
        if got != expected:
            raise ValueError(
                "line %r has %d syllables, expected %d" % (line, got, expected)
            )
    if not 1 <= len(haiku) <= MAX_LENGTH:
        raise ValueError("haiku must be 1-200 characters, got %d" % len(haiku))


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    check_haiku(HAIKU)
    out_dir = output_dir()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    # Write to a temp file in the same directory, then move it into
    # place so the entry is never seen half-written.
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(HAIKU)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    os.chmod(target, 0o644)

    # Read it back and confirm it is exactly what we meant to write,
    # byte for byte, with no stray newline or encoding surprise.
    with open(target, "rb") as handle:
        raw = handle.read()
    if raw != HAIKU.encode("utf-8"):
        raise ValueError("verification failed: entry.txt does not match the haiku")
    if raw.endswith(b"\n"):
        raise ValueError("verification failed: entry.txt has a trailing newline")
    mode = stat.S_IMODE(os.stat(target).st_mode)
    if mode != 0o644:
        raise ValueError("verification failed: entry.txt mode is %o" % mode)
    check_haiku(raw.decode("utf-8"))
    counts = [count_syllables(line) for line in HAIKU.split("\n")]
    print(
        "wrote %d characters (%s) to %s"
        % (len(HAIKU), "-".join(str(c) for c in counts), target)
    )


if __name__ == "__main__":
    main()
