"""Entrypoint for the news-image-20261119 entry.

Renders the poster with make_image (pure stdlib) and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png, defaulting to /output/entry.png in the
grading sandbox. No network, no input files: the image is drawn fresh
on every run, so both runs produce identical bytes.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from make_image import build_entry


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    size = build_entry(target)
    print("wrote %s (%d bytes)" % (target, size))


if __name__ == "__main__":
    main()
