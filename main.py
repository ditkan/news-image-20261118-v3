#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261118.

Copies the shipped front-page image (entry.png, drawn programmatically
by render.py during the build session) to $MAKEFUN_OUTPUT_DIR/entry.png.
Standard library only; deterministic -- the same bytes on every run.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
