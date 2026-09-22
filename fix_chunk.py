#!/usr/bin/env python3

import argparse
import os
import struct
import sys
import zlib

LEN_START, LEN_END = 5, 9      # offsets 5-8   -> length (4 bytes, big-endian)
CRC_START, CRC_END = 9, 17     # offsets 9-16  -> stored CRC (8 bytes, big-endian)
BODY_START = 17                # offsets 17-end -> body


def main():
    parser = argparse.ArgumentParser(description="Repair CRC header field of a PZ chunk .bin")
    parser.add_argument("file", help="path to the blam .bin file (e.g. 324.bin)")
    parser.add_argument("--save", type=int, required=True, help="save= value from the error txt")
    parser.add_argument("--load", type=int, required=True, help="load= value from the error txt")
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

    if len(data) < BODY_START + 1:
        print("FAIL: file is too small to be a valid chunk.")
        sys.exit(1)

    file_size = len(data)
    stored_len = struct.unpack(">I", data[LEN_START:LEN_END])[0]
    stored_crc = struct.unpack(">Q", data[CRC_START:CRC_END])[0]
    body_crc = zlib.crc32(data[BODY_START:]) & 0xFFFFFFFF

    print(f"File:             {args.file}")
    print(f"File size:        {file_size}")
    print(f"Length in header: {stored_len}")
    print(f"Stored CRC:       {stored_crc}")
    print(f"Body CRC32:       {body_crc}")
    print(f"save= (given):    {args.save}")
    print(f"load= (given):    {args.load}")
    print()

    check1 = stored_len == file_size
    check2 = stored_crc == args.save
    check3 = body_crc == args.load

    print(f"[{'PASS' if check1 else 'FAIL'}] 1) length in header == file size")
    print(f"[{'PASS' if check2 else 'FAIL'}] 2) stored CRC == save= value")
    print(f"[{'PASS' if check3 else 'FAIL'}] 3) body CRC32 == load= value")
    print()

    if not (check1 and check2 and check3):
        print("NOT SAFE to repair. At least one check failed, so no file was written.")
        print("(This may be a different problem, or the body itself may be corrupt. Do not replace anything.)")
        sys.exit(2)

    # All checks passed -> overwrite ONLY the 8-byte CRC field with the load= value
    fixed = bytearray(data)
    fixed[CRC_START:CRC_END] = struct.pack(">Q", args.load)

    # Verify that only the CRC field changed
    changed = [i for i in range(file_size) if fixed[i] != data[i]]  # 0-indexed offsets
    if any(not (CRC_START <= i < CRC_END) for i in changed):
        print("ERROR: a byte outside the CRC field changed. Not saving.")
        sys.exit(3)

    base, ext = os.path.splitext(args.file)
    out_path = f"{base}_fixed{ext}"
    with open(out_path, "wb") as f:
        f.write(fixed)

    print("ALL CHECKS PASSED. Safe to repair.")
    print(f"Offsets changed: {changed}")
    print(f"Saved: {out_path}")
    print()
    print("Next steps:")
    print(f"  - Rename '{os.path.basename(out_path)}' back to '{os.path.basename(args.file)}'")
    print("  - Stop the server before replacing the live map/<wx>/<wy>.bin")
    print("  - Back up the current live file first")


if __name__ == "__main__":
    main()
