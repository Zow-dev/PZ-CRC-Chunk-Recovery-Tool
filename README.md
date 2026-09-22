# Project Zomboid Chunk CRC Recovery By Zow

This guide explains how to verify and repair a Project Zomboid `.bin` chunk from the server's `blam` folder when the server reports a CRC mismatch.

> **Important:** Only use this procedure for chunks that match the CRC-mismatch pattern described below. Always make a backup before replacing any live chunk.

## 1. Extract the Recovery Package

Extract the provided ZIP file.

After extraction, a folder named:

```text
PZ CRC Chunk Recovery/
```

will be created automatically.

The folder contains the recovery script:

```text
PZ CRC Chunk Recovery/
└── fix_chunk.py
```

Copy the affected `.bin` file from the server's `blam` folder into this folder.

For example:

```text
PZ CRC Chunk Recovery/
├── fix_chunk.py
└── 283.bin
```

> **Work on a copy of the `.bin` file. Do not copy or modify the original `.blam` file directly.**

The repair script **does not modify the original `.bin` file**. It creates a new `_fixed.bin` file and changes only the 8-byte CRC field in the header.

## 2. Requirements

* Python 3
* A dedicated recovery folder
* `fix_chunk.py` inside the recovery folder
* The affected `.bin` file copied from the server's `blam` folder
* The `save=` and `load=` values from the corresponding error log

## 3. Find the CRC Mismatch in the Server Log

Look for an error similar to:

```text
SANITY CHECK FAIL! thread="LoadChunk"
CRC mismatch save=0 load=3737262551
...
load wx,wy=1512,283
```

Record the exact:

```text
save=0
load=3737262551
```

Also identify the affected chunk coordinates.

## 4. Locate the Corresponding `.blam` File

Find the corresponding chunk inside the server's `blam` folder.

For example:

```text
blam/
└── 1512/
    └── 283.bin
```

**Do not delete or overwrite the original `.blam` file.**

## 5. Run the Repair Script

From the directory containing `fix_chunk.py`, run:

```bash
python fix_chunk.py 283.bin --save 0 --load 3737262551
```

Replace the filename and CRC values with the values from your actual error.

For example:

```bash
python fix_chunk.py 283.bin --save 0 --load 3006569527
```

## 6. The Script Performs Three Safety Checks

The repair will only proceed if **all three checks pass**:

```text
[PASS] 1) length in header == file size
[PASS] 2) stored CRC == save= value
[PASS] 3) body CRC32 == load= value
```

These checks verify that:

1. The length stored in the header matches the actual file size.
2. The CRC currently stored in the file matches the `save=` value from the error.
3. The CRC calculated from the chunk body matches the `load=` value from the error.

If any check fails, the script will **not create a repaired file**.

```text
NOT SAFE to repair. At least one check failed, so no file was written.
```

Do not replace the live chunk if this happens.

## 7. Check the Generated File

If all checks pass, the script creates:

```text
283_fixed.bin
```

The script verifies that the **only bytes changed are offsets 9–16**, which contain the stored CRC.

### Chunk Header Layout

Offsets are zero-indexed:

```text
0–4     Signature / other header data
5–8     File length (4 bytes, big-endian)
9–16    Stored CRC (8 bytes, big-endian)
17–end  Chunk body
```

Only offsets `9–16` are modified.

## 8. Back Up the Live Chunk

Before replacing anything:

1. Stop the Project Zomboid server.
2. Make a backup of the current live `.bin` file.
3. Keep the original `.blam` file.
4. Keep the generated `_fixed.bin` file.

Do not overwrite your only copy.

## 9. Replace the Affected Chunk

After the server is stopped and the live chunk has been backed up:

1. Rename the repaired file back to the original filename.
2. Replace the affected live chunk in the appropriate `map/<wx>/<wy>.bin` location.
3. Start the server.
4. Check the affected area in-game.

Example:

```text
Repaired:
283_fixed.bin

Rename to:
283.bin
```

Then replace the corresponding live file:

```text
map/1512/283.bin
```

## 10. Verify the Recovery

After starting the server, check the affected area.

If the CRC mismatch was the only problem and the chunk body was intact, the player's structures and other chunk data should be restored.

## Important Limitations

This procedure is specifically for the CRC/header mismatch pattern that passes all three checks.

It does **not** prove that every corrupted chunk is recoverable.

If:

* the header length does not match the file size;
* the stored CRC does not match the `save=` value;
* the calculated body CRC does not match the `load=` value; or
* the chunk has other corruption;

**do not replace the live chunk using this method.**

Keep the original file and investigate the affected chunk separately.

## What the Repair Actually Does

The repair does **not rebuild the chunk** and does not regenerate the map.

It takes the existing chunk data and replaces only the incorrect CRC value in the header:

```text
Before:

[Header]
CRC = incorrect / 0

[Chunk Body]
Existing player/world data


After:

[Header]
CRC = matching load= value

[Chunk Body]
Same exact data
```

This is why the method can recover a player-built area when the chunk body itself is still intact.

---

# Credits

### CRC Issue / Original Discovery

Credit to the Indie Stone forum community for the investigation and documentation of the underlying Project Zomboid Build 42.20.4 CRC issue, including the behavior involving incorrect or zero CRC values in chunk headers and subsequent `SANITY CHECK FAIL` / `CRC mismatch` errors.

Original discussion:

https://theindiestone.com/forums/topic/100901-42204-mp-shared-crc32-instances-in-the-chunk-save-pipeline-race-across-threads-chunk-headers-are-written-with-a-wrong-or-zero-crc-and-the-next-load-answers-sanity-check-fail-with-blam-loadbrandnew-wiping-player-built-chunks/#findComment-490287

### Recovery Tool

**`fix_chunk.py` — created by Zow**

The recovery script was created as a **CRC header corrector** based on the documented CRC mismatch behavior.

The tool performs safety checks against the reported `save=` and `load=` values and, when all checks pass, creates a repaired copy with the stored CRC in the chunk header corrected.

The chunk body itself is not rebuilt or modified.

---

## Disclaimer

`PZ CRC Chunk Recovery` is an unofficial, community-created tool and is **not affiliated with, endorsed by, or supported by The Indie Stone**.

This tool was created by **Zow** to assist with recovery of specific Project Zomboid chunk CRC/header mismatch cases. It is intended as a temporary recovery workaround for affected chunks while the underlying `save=` / `load=` CRC issue remains present.

This tool is provided as-is and without any guarantee of successful recovery.

Always create a full backup of your server save before modifying any files. **Zow and the contributors to this tool are not responsible for data loss, corrupted saves, lost player progress, or any other damage resulting from the use or misuse of this tool.**

The tool does not modify the original input file. It creates a repaired copy and only attempts to correct the stored CRC value when its safety checks pass.

This recovery method should only be used for the specific CRC mismatch pattern described in this guide. It should not be treated as a general-purpose solution for corrupted Project Zomboid chunks.

The Project Zomboid game, its trademarks, and related intellectual property remain the property of their respective owners.

