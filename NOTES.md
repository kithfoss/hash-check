# hash-check — Build Notes

## Week 37 — seeded + built 2026-08-14

### Why this tool

EXPERIMENTS.md queue was exhausted — all seeded ideas had shipped. Needed a Week 37 candidate. `hash-check` fills a real gap: verifying a download checksum is tedious with bare `sha256sum` (manual string comparison, no exit code on mismatch). This collapses compute + verify into one command with clean semantics.

### Design choices

**Algorithm detection from digest length:** When `--verify` gets a bare hex string (no prefix), we infer the algorithm from the character count — 32 = MD5, 40 = SHA-1, 64 = SHA-256, 128 = SHA-512. This means `hash-check file --verify e3b0c44...` just works without an explicit flag.

**Prefix takes priority:** `SHA256:abc` in `--verify` overrides any explicit algorithm flag. Makes copy-pasting from release pages frictionless — you don't have to manually add `--sha256`.

**Exit codes:** 0 = OK or computed, 1 = mismatch, 2 = usage/file error. This is the right split for scripting: `if hash-check file --verify HASH --quiet; then ...` reads naturally.

**Streaming:** Reads files in 64KB blocks to handle large files without loading them into memory. Stdin is also streamed via binary read.

**Output format:** `ALGO  digest  file` mirrors `sha256sum` output, which is the convention. Makes it readable alongside existing tooling.

### What works

- 37 tests passing
- All four algorithms (MD5, SHA-1, SHA-256, SHA-512)
- Algorithm auto-detection from prefix and digest length
- Quiet mode + JSON mode
- Stdin support (`-`)
- Large file streaming (tested at 5MB)
- Empty file edge case

### What's not done yet

- No batch mode (multiple files in one invocation) — deferred; not needed for v0.1.0
- No `--check FILE` to read a sha256sum-style checksum file — would be a useful v0.2 feature

### Ship checklist

- [x] Implementation complete
- [x] 37 tests, all passing
- [x] README complete
- [x] NOTES complete
- [x] Committed to workspace repo (2026-08-15)
- [ ] GitHub repo created and v0.1.0 tagged — blocked by invalid GH_TOKEN (same pattern as previous tools; resolve token and push)

### Next

When GH_TOKEN is valid:
```sh
gh repo create kithfoss/hash-check --public --source . --push
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 --title "hash-check v0.1.0" --notes "Compute and verify file checksums. 37 tests, stdlib only."
```
