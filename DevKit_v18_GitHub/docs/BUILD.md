# Building DevKit v18 from source

## Environment verified during preparation

- Ubuntu 24.04 userspace on x86-64 Linux.
- Python 3.12.14; zlib 1.3.2.
- GCC 13.3.0 (`Ubuntu 13.3.0-6ubuntu2~24.04`).
- GNU ld 2.42, with the `i386pe` emulation.
- No pip dependencies and no Windows executables.

GCC must accept `-m32` for compiling the DLL C file. The DLL C file uses no external C headers or runtime library; the native test executable uses the ordinary host C library. The included linker helper converts the GCC ELF object to COFF and creates import libraries for the explicitly listed Windows APIs. Those build-only import-library stubs are never included in the mod.

## Commands

From the repository root:

```sh
python3 scripts/build.py --strict-original
python3 -m unittest discover -s tests -v
```

The first command rebuilds three DATs, the SCR, sixteen GIs, ModuleInfo and the x86 DLL. It runs the native C unit tests, checks every output SHA-256 against the reference manifest and writes a ZIP plus `build-report.json` to `dist/`.

The second command includes an independent source-only rebuild in a temporary directory. No `original/` directory or prebuilt DLL is copied into that directory. It also tests that editing RSON code and variable initialization affects the compiled script, and verifies graphics roundtrips and a pixel edit.

Without `--strict-original`, the build still checks the runtime file list and ZIP integrity and reports any different hashes. This supports deliberate source edits and toolchain variation. Exact reproduction of the supplied release was verified with the environment listed above.

## Script source and serializer

```sh
python3 scripts/scr_codec.py source/script/Mod_DevKit.rson dist/Mod_DevKit.scr
python3 scripts/inspect_scr.py dist/Mod_DevKit.scr --output dist/Mod_DevKit.inspect.json
```

`scr_codec.py` reads `Mod_DevKit.layout.json` automatically beside the RSON. A layout record such as `["wstr", 27, "Name"]` writes a null-terminated UTF-16LE field from object #27. `lines` joins a `Code` array with LF; the recovered lines retain original CR characters where present. `offset` and `mark` recalculate the global/local section boundary. Integer, boolean, float and string values remain editable in the RSON.

The layout records preserve the release's variable ordering, dialog indices and object bindings. Preserve them when editing existing code. New object structures must be added to the layout explicitly. The serializer performs the same binary-format step needed by the game loader; CodeEC compilation happens inside the game, as it does for the original SCR.

This source build does not depend on reconstructing the original visual authoring graph. Standard RScript opening/recompilation of the regenerated scene remains unexecuted and is not part of the verified build path.

## Graphics source

`source/graphics/layers/<name>.json` contains RGB565 color samples, 6-bit transparency values, layer bounds, reserved fields and explicit RLE run packets. These are the lossless build inputs. PNGs are visual references; editing a preview PNG alone does not change the release.

```sh
python3 scripts/gi_codec.py encode source/graphics/layers/DevKitArrowA.json dist/DevKitArrowA.gi
```

## Configuration source

`Main.json`, `CacheData.json` and `Lang.json` preserve the complete BlockPar trees, metadata, cipher seeds and compression parameters. `scripts/dat_codec.py` provides the independent source encoder and decoder. Readable `.txt` files are references, not duplicate authoritative build inputs.

## Outputs

- `dist/mod/DevKit/`: rebuilt mod directory.
- `dist/DevKit_v18_FROM_SOURCE.zip`: installable mod ZIP.
- `dist/build-report.json`: build environment, hash comparison and package hash.

The archive installs at `Mods/Tweaks/DevKit` and requires `UtilityFunctionsPack`. Game testing is outside the checks performed during this source preparation.
