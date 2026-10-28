# Technical note for Nexus Mods review

This repository contains reconstructed editable source and build tools for the supplied DevKit v18 release for Space Rangers HD: A War Apart.

All 22 runtime files were rebuilt from source on 28 October 2026. Every output SHA-256 matched the original release: the SCR, DLL, three DAT files, sixteen GI files and ModuleInfo. The build was also repeated in an isolated directory containing no original runtime binaries. See `docs/build-report.json`, `docs/test-results.txt` and `original-file-sha256.json`.

The script's complete stored source text and runtime definitions are in `source/script/Mod_DevKit.rson`. Its explicit typed serialization order is in `Mod_DevKit.layout.json`. The Python serializer is included and does not need RScript, Windows, the game executable, or opaque precompiled script payloads. A separate inspector reads the resulting SCR into named fields for comparison.

The DLL's C source, tests and build scripts are in `source/native/wheel/`. It exports `WheelEnable` and `WheelDisable`, installs a message hook scoped to the invoking UI thread, and translates mouse-wheel messages over the configured rectangle into Page Up / Page Down key messages. Its declared Windows API imports and callback behavior are visible in source and covered by host-side C tests.

All configuration and graphics build inputs are editable. Source provenance, original author credits and format research are documented in `AUTHORS.md` and `docs/FORMAT_NOTES.md`. The separate `original/` directory preserves release artifacts for comparison.

The original visual-editor coordinates were unavailable and have been regenerated. Direct opening/recompilation of the reconstructed scene in RScript was not executed; the supplied native Python source build is the verified reproduction path. The preparation included no game execution, antivirus verdict or moderation decision. Existing TEST status is retained.
