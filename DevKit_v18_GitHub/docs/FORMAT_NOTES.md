# Format provenance and source representation

## SCR8

The binary layout was studied in the previously supplied Space Rangers HD engine research snapshot, particularly:

- [pakompom/SpaceRangersHD_decomp](https://github.com/pakompom/SpaceRangersHD_decomp), `source/script/aScript.pas`: `TScript.LoadFromBuffer`, `CompileScriptTemplateCondition`.
- `source/script/EC_Expression.pas`: `TVarEC.LoadFromBuffer`.
- `source/resources/EC_Buf.pas`: null-terminated UTF-16LE string handling.

The serializers and inspector in this project were implemented in Python for this recovery. They do not bundle engine source or a game executable. The full SCR8 stores source text and typed data; no game-language bytecode needed to be reverse-compiled.

The RSON object structure was checked against previously supplied RSON examples from `Space-Rangers-Mods-Sources` and with the supplied SRHD-XenoModKit 0.10.4. Existing code text and comments were preserved. Diagram layout was regenerated. `DevKit.*` properties keep runtime fields that otherwise lack an unambiguous visual field in the recovered scene.

The `Mod_DevKit.layout.json` sidecar is part of the source build: each record names a primitive and a RSON field, or a small structural constant such as a section count. It contains no original SCR payload, encoded code blob, or hidden executable data.

## DAT

`scripts/dat_codec.py` is the previously prepared standard-library codec. The format was studied using Sergei Osminin's MIT-licensed [murgesku/rangers-utils](https://github.com/murgesku/rangers-utils): ZL01 + zlib compression, Park-Miller stream cipher, CRC32, UTF-16LE strings and sorted BlockPar metadata. No third-party library is required at build time.

## GI

The GI2 format was checked using the supplied [SRHD-XenoModKit](https://github.com/Xenomorphchyma/SRHD-XenoModKit) image codec. `scripts/gi_codec.py` independently exposes header fields, descriptors, RLE packets, RGB565 samples and transparency values as JSON. It preserves all original pixels and encoding details. Preview PNGs were recovered in the prior project and confirmed against the original GI images.

No third-party Windows editor binaries are distributed in this source package. These format acknowledgments do not assign a license to the mod or change existing authorship.
