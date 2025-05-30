#!/usr/bin/env python3
"""
convert_gbmp_to_zip.py

Reads an input file 1 bytes at a time and checks 4 bytes chunks. 
If a 4-byte chunk equals 0x47 42 4D 50 (“GBMP”),
it is replaced with 0x50 4B 03 04 (“PK\x03\x04”) in the output.  
The output is written next to the original file, but with a .zip suffix.
Afterwards the script checks the resulting file is a valid ZIP archive.
"""

import sys
from pathlib import Path
import zipfile

PATTERN      = bytes.fromhex("47424D50")   # GBMP
REPLACEMENT  = bytes.fromhex("504B0304")   # PK..

def convert(src: Path) -> Path:
    """
    Read *src* **one byte at a time** and write a new file where every
    occurrence of PATTERN is replaced by REPLACEMENT.  
    Returns the path to the newly created .zip file.
    """
    dst = src.with_suffix(".zip")

    buf = bytearray()                       # rolling window (≤ 4 bytes)
    with src.open("rb") as fin, dst.open("wb") as fout:
        while (b := fin.read(1)):           # read exactly 1 byte
            buf += b                        # append to window

            if len(buf) < 4:
                # Not enough for a possible match yet – keep reading
                continue

            if buf == PATTERN:
                # Exact 4-byte signature found ➜ write replacement
                fout.write(REPLACEMENT)
                buf.clear()                 # reset window
            else:
                # First byte cannot be part of a match ➜ flush it
                fout.write(bytes((buf[0],)))
                del buf[0]                  # keep last 3 bytes

        # EOF – flush anything left in the window
        if buf:
            fout.write(buf)

    return dst

def is_valid_zip(path: Path) -> bool:
    """Return True only if *path* is a healthy ZIP archive."""
    if not zipfile.is_zipfile(path):
        return False
    with zipfile.ZipFile(path) as zf:
        return zf.testzip() is None      # testzip() → None means no CRC errors

def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <input_file>")
        sys.exit(1)

    src = Path(argv[1])
    if not src.is_file():
        sys.exit(f"Error: {src} does not exist or is not a file.")

    dst = convert(src)

    if is_valid_zip(dst):
        print(f"Success: wrote valid ZIP → {dst}")
        sys.exit(0)
    else:
        sys.exit(f"Warning: {dst} is not a valid ZIP archive.")

if __name__ == "__main__":               # pragma: no cover
    main(sys.argv)
