#!/usr/bin/env python3
"""Copy the entry image to the output directory.

Reads entry.png next to this script, verifies it is a PNG of at most
1 MiB, and writes it to /output/entry.png (or to a path given as the
first command-line argument). Exits non-zero with a clear message on
any failure.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WANT_WIDTH = 1024
WANT_HEIGHT = 1024


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    dest = argv[1] if len(argv) > 1 else "/output/entry.png"

    if not os.path.isfile(source):
        return fail(f"entry image not found: {source}")

    with open(source, "rb") as handle:
        data = handle.read()

    if len(data) > MAX_BYTES:
        return fail(f"entry image is {len(data)} bytes, over the 1 MiB limit")
    if data[:8] != PNG_MAGIC:
        return fail("entry image does not start with the PNG magic bytes")
    if len(data) < 33 or data[12:16] != b"IHDR":
        return fail("entry image has no PNG IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (WANT_WIDTH, WANT_HEIGHT):
        return fail(f"entry image is {width}x{height}, expected 1024x1024")

    out_dir = os.path.dirname(dest)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(dest, "wb") as handle:
        handle.write(data)

    with open(dest, "rb") as handle:
        copied = handle.read()
    if hashlib.sha256(copied).hexdigest() != hashlib.sha256(data).hexdigest():
        return fail("copied file does not match the entry image")

    print(f"wrote {dest} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
