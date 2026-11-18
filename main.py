#!/usr/bin/env python3
"""news-image-20261118 entry (Python 3.13, standard library only).

The entry image is the entry.png beside this file: a one-page newspaper
front page summing up the world's news of Wednesday 18 November 2026,
drawn in code by render.py (also in this repository). This program copies
it to /output/entry.png. It uses no network and writes the same bytes on
every run.

Local run:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(
        os.path.join(HERE, "entry.png"),
        os.path.join(out_dir, "entry.png"),
    )


if __name__ == "__main__":
    main()
