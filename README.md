# hash-check

Compute and verify file checksums.

```
hash-check file.tar.gz
hash-check file.tar.gz --verify SHA256:abc123...
hash-check file.tar.gz --md5
cat archive.tar.gz | hash-check -
```

## Why

"Did this download arrive intact?" and "is this the file I expect?" are constant questions when dealing with releases, build artifacts, and backups. `sha256sum` and `md5sum` both answer parts of it, but verifying against a known hash still requires a manual string comparison or a shell one-liner. `hash-check` wraps the full compute-and-verify workflow into one command with a clean exit code.

## Install

```sh
cp hash_check.py ~/.local/bin/hash-check
chmod +x ~/.local/bin/hash-check
```

Or with a symlink:

```sh
ln -s "$(pwd)/hash_check.py" ~/.local/bin/hash-check
```

## Usage

```
hash-check [FILE]                    compute checksum (default: SHA-256)
hash-check FILE --verify HASH        verify against expected hash
hash-check -                         read from stdin
```

### Options

| Flag | Description |
|------|-------------|
| `--verify HASH` | expected hash to compare against |
| `--md5` | use MD5 |
| `--sha1` | use SHA-1 |
| `--sha256` | use SHA-256 (default) |
| `--sha512` | use SHA-512 |
| `--quiet`, `-q` | suppress output; use exit code only |
| `--json` | output as JSON |

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Hash computed (no verify), or hash matched |
| 1 | Hash mismatch |
| 2 | Usage error or file not found |

### HASH format for `--verify`

You can pass the hash with or without an algorithm prefix:

```
SHA256:abc123...    algorithm prefix (takes precedence over flags)
MD5:abc123...
abc123...           bare hex — algorithm inferred from digest length, or from flags
```

## Examples

Compute SHA-256:

```
$ hash-check archive.tar.gz
SHA256  e3b0c44298fc...  archive.tar.gz
```

Verify a download (exact-match check):

```
$ hash-check archive.tar.gz --verify SHA256:e3b0c44298fc...
OK  SHA256  archive.tar.gz
```

Mismatch:

```
$ hash-check archive.tar.gz --verify SHA256:aaaaaaaaaa...
MISMATCH  SHA256  archive.tar.gz
  expected: aaaaaaaaaa...
  got:      e3b0c44298fc...
$ echo $?
1
```

Quiet mode for scripts:

```sh
if hash-check "$FILE" --verify "$EXPECTED" --quiet; then
  echo "verified"
else
  echo "FAILED" >&2
  exit 1
fi
```

JSON output:

```
$ hash-check file.txt --json
{
  "file": "file.txt",
  "algorithm": "sha256",
  "digest": "e3b0c44298fc..."
}

$ hash-check file.txt --verify SHA256:e3b0c44... --json
{
  "file": "file.txt",
  "algorithm": "sha256",
  "digest": "e3b0c44298fc...",
  "expected": "e3b0c44298fc...",
  "match": true
}
```

Stdin:

```
$ cat release.tar.gz | hash-check -
SHA256  e3b0c44298fc...  -
```

## Requirements

- Python 3.6+
- No external dependencies (stdlib `hashlib`)

## Limitations

- No parallel hashing of multiple files in one invocation — pipe multiple calls or use a shell loop.
- Stdin mode reads the entire stream into memory if the hash is needed for verification with a prefix; otherwise it streams.

## Earn model

Free.
