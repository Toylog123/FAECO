# s820 full evidence solid 7z archive

This archive contains all files under the nine completed s820 jobs and inputs/s820,
the fixed manifest/preflight/frozen audit, the registered 44 runtime source files,
actual Liberty and s820 RTL. It is not an archive of the full 72-job matrix.
The supplied frozen audit has actual case counts {'s27': 9, 's382': 9, 's420': 9, 's641': 9, 's713': 9, 's820': 9, 's832': 9, 's953': 9}.
Only this case's nine independently accepted jobs are archived here.

Keep every .7z.NNN volume together. Verify each size/SHA against receipt.json.
The whole-archive SHA is the SHA256 of concatenated volume bytes in numeric order.
Each volume is at most 80 MiB. Solid LZMA2 is deliberate; do not substitute ZIP.

Use a NEW empty restore directory, never an existing experiment checkout:

    7z t s820_full_evidence.7z.001
    7z x s820_full_evidence.7z.001 -o<NEW_RESTORE_REPOSITORY_ROOT>

Archive entries begin with repository-relative code/, data/, experiments/ or
project_docs/. No absolute drive prefix or traversal member is used. Restoration
does not require the original D: drive. Compare each extracted file SHA/size with
source_before.json; archive_members.json records exact member sizes. A full
independent scratch extraction was already compared byte-for-byte by SHA/size.

Historical Tcl/JSON argv may contain original absolute runtime paths. Those bytes
are evidence and were not rewritten; the archive is a portable byte restoration,
not permission or a claim that old EDA commands rerun without explicit rebinding.
Tool executables, WSL environment and external tool installation are not bundled.
No new STA/SEC/mapping was run. The original experiments were read only. Existing
outputs and archives are never overwritten/resumed. All creation/test/list/restore
commands, versions, bounded timeouts, logs and hashes are in receipt.json.
