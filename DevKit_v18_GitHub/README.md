# DevKit v18 — complete reconstructed source

Source package for Space Rangers HD: A War Apart, prepared for GitHub and Nexus Mods review.

**Verified on 28 October 2026: all 22 runtime files rebuild from editable source with exactly the same SHA-256 hashes as the supplied DevKit v18.** The source-only test builds successfully after every reference `.scr`, `.dat`, `.gi` and `.dll` has been excluded from the build directory.

[Русское описание](README_RU.md) · [Build instructions](docs/BUILD.md) · [Nexus review note](docs/NEXUS_REVIEW.md) · [Verification](docs/VERIFICATION.md)

## Source map

| Source | Output | Verified result |
| --- | --- | --- |
| `source/script/Mod_DevKit.rson` + `Mod_DevKit.layout.json` | `Mod_DevKit.scr` | 253,142 bytes; exact original SHA-256 |
| `source/config/{Main,CacheData,Lang}.json` | Three DAT files | All byte-identical |
| `source/native/wheel/devkit_wheel.c` | `DevKitWheel.dll` | Byte-identical; native unit tests pass |
| `source/graphics/layers/*.json` | Sixteen GI files | All byte-identical |
| `source/module/ModuleInfo.txt` | Runtime `ModuleInfo.txt` | Byte-identical UTF-16 output |

`source/graphics/*.png` provides readable image previews. The layer JSON stores the exact RGB565 pixels, transparency samples, bounds and RLE packets used by the original graphics. `source/config/readable/` provides text views of the editable DAT trees; the JSON files are the build inputs.

`original/DevKit/` contains the 22 unmodified reference files in a separate directory. `original-file-sha256.json` records their identities. The build reads source and the hash manifest; it does not copy runtime binaries from `original/`.

## Build

On Linux, with Python 3.10+, GCC and GNU binutils installed:

```sh
python3 scripts/build.py --strict-original
python3 -m unittest discover -s tests -v
```

The output is `dist/DevKit_v18_FROM_SOURCE.zip`, with a machine-readable `dist/build-report.json`. No Python packages, Windows applications, game installation or network downloads are needed. A GitHub Actions workflow is included; its hosted run has not been performed in this preparation session.

## Recovered script format

SCR version 8 contains source strings and runtime definitions. The complete file was parsed using the game's documented/reconstructed loader structure. All stored code, variables, world bindings, states and dialogs were recovered. The RSON scene contains 4 dialogs, 14 messages and 78 answers. Original visual node positions were unavailable and have been regenerated.

`scripts/scr_codec.py` reads executable source from the RSON object fields. The accompanying layout describes typed SCR8 serialization order and refers to those fields by object ID. It contains no opaque compiled-code payload. Editing an existing `Code`, `Msg`, variable initializer or mapped world field changes the rebuilt SCR.

The included encoder is specific to this reconstructed DevKit runtime model. Adding/removing graph objects requires updating the explicit layout too; it is not a general replacement for the RScript visual-graph compiler. Opening or compiling this reconstructed scene in RScript 4.15f was not executed. The included source build is independently verified and does not require RScript.

## Installation and runtime status

The built ZIP contains `DevKit/`; its installation location is `Mods/Tweaks/DevKit`. The module declares `UtilityFunctionsPack` as a dependency. Existing author credits `noname, Prolog_D` are retained.

The supplied mod identifies itself as a TEST build. Source reconstruction changes no runtime bytes. Game execution and Nexus moderation approval have not been performed or claimed.
