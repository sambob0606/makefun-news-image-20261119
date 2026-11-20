"""Entry program for news-image-20261119 (Python 3.13, standard library only).

The image is stored in the repository as entry_image.b64 (one line of
base64, produced by make_image.py from the verified 19 November 2026
headlines). This program decodes it to /output/entry.png. No network,
no randomness: two runs write the same bytes.
"""
import base64
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    data = base64.b64decode((HERE / "entry_image.b64").read_text(encoding="ascii"))
    # The grader sets /output; MAKEFUN_OUTPUT_DIR is the local stand-in.
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)


if __name__ == "__main__":
    main()
