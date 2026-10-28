# Recovered DevKit v18 configuration sources

These are **fully recovered** editable DAT sources. JSON files (Main.json, CacheData.json, Lang.json) are the canonical inputs for `scripts/dat_codec.py`. The files in `readable/` are UTF-8 human-readable reference exports, not separate build inputs. The JSON includes record ordering, sorted BlockPar grouping metadata, the original encryption seed, and every string.

From the repository root:

```sh
python scripts/dat_codec.py encode source/config/Main.json /tmp/Main.dat
python scripts/dat_codec.py verify source/config/Main.json original/DevKit/CFG/Main.dat
python scripts/build.py --strict-original
```

All three regenerated DAT files compare **byte-for-byte** against the originals in this repository. No external BlockParEditor is needed for this conversion. The codec uses Python's standard library and the binary-format conventions documented by MIT-licensed [`rangers-utils`](https://github.com/murgesku/rangers-utils) (Sergei Osminin, 2020).

**Changes:** Edit JSON `value` strings for parameters. Structural additions/removals may require updates to `sort_meta` in sorted blocks; the codec preserves original sort metadata rather than quietly inventing binary structures. Validate and compare the resulting DAT before using it in-game.
