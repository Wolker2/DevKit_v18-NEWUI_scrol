# Verification — 28 October 2026

Input: `DevKit_v18 NEWUI_scrol(1).rar`, structurally a ZIP archive.

Input archive SHA-256: `379010b977a20230ba1fcb05725166c73329e071d93ee036ca42cecc71fe4ee9`.

## Completed checks

| Check | Result |
| --- | --- |
| Input ZIP integrity | PASS |
| Original runtime manifest | 22 files match |
| Complete SCR parsing | 253,142 / 253,142 bytes consumed; no unparsed tail |
| Recovered RSON structure | SRHD-XenoModKit 0.10.4 modern-cli validation: 0 issues |
| RSON + typed layout -> SCR | Byte-identical original SHA-256 |
| Independent SCR inspection | All parsed fields equal the original |
| RSON code edit | Rebuilt code changes; section offset recalculated correctly |
| RSON variable edit | Rebuilt initialization changes correctly |
| Three JSON -> DAT rebuilds | All byte-identical |
| Sixteen layer JSON -> GI rebuilds | All byte-identical |
| GI source pixel edit | Encoded/decoded sample change retained |
| C DLL unit tests | PASS |
| C source -> DLL | Byte-identical original SHA-256 |
| Source-only complete rebuild | PASS without any original/prebuilt runtime binary |
| Runtime package CRC and hashes | PASS; 22/22 match |

The five Python tests and native C tests were run locally. `docs/test-results.txt` captures their output; `docs/build-report.json` records hashes and tool versions. GitHub Actions configuration is included, but a hosted run has not been executed.

## Limits of these results

The verified SCR path uses the included Python serializer and the explicit layout. The reconstructed RSON has regenerated visual positions. RScript's own GUI/graph-compiler compatibility was not executed, so no RScript-specific roundtrip is claimed.

The full source rebuild preserves the original mod bytes and its original TEST status. Game execution, live Windows hook behavior, antivirus scanning and Nexus moderation approval were not performed.
