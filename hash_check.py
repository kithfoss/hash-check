#!/usr/bin/env python3
"""hash-check — compute and verify file checksums."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}

BLOCK_SIZE = 65536


def hash_file(path, algorithm):
    h = ALGORITHMS[algorithm]()
    if path == "-":
        data = sys.stdin.buffer.read()
        h.update(data)
    else:
        with open(path, "rb") as f:
            while True:
                block = f.read(BLOCK_SIZE)
                if not block:
                    break
                h.update(block)
    return h.hexdigest()


def parse_expected(expected_str):
    """Parse 'SHA256:abc123' or bare 'abc123' into (algorithm_or_None, hex)."""
    for algo in ALGORITHMS:
        prefix = algo.upper() + ":"
        if expected_str.upper().startswith(prefix):
            return algo, expected_str[len(prefix):]
    return None, expected_str


def detect_algo_from_hex(hex_str):
    """Guess algorithm from hex digest length."""
    n = len(hex_str)
    if n == 32:
        return "md5"
    if n == 40:
        return "sha1"
    if n == 64:
        return "sha256"
    if n == 128:
        return "sha512"
    return None


def main():
    parser = argparse.ArgumentParser(
        prog="hash-check",
        description="Compute and verify file checksums.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hash-check file.tar.gz
  hash-check file.tar.gz --verify SHA256:abc123...
  hash-check file.tar.gz --md5
  cat file.tar.gz | hash-check -
  hash-check file.tar.gz --json
""".strip(),
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="file to hash, or - to read stdin (default: -)",
    )
    parser.add_argument(
        "--verify",
        metavar="HASH",
        help="expected hash to compare against (e.g. SHA256:abc123 or bare hex)",
    )

    algo_group = parser.add_mutually_exclusive_group()
    algo_group.add_argument("--md5", action="store_true", help="use MD5")
    algo_group.add_argument("--sha1", action="store_true", help="use SHA-1")
    algo_group.add_argument("--sha256", action="store_true", help="use SHA-256 (default)")
    algo_group.add_argument("--sha512", action="store_true", help="use SHA-512")

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="suppress output; use exit code only (requires --verify)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="output as JSON",
    )

    args = parser.parse_args()

    # Determine algorithm
    if args.md5:
        algorithm = "md5"
    elif args.sha1:
        algorithm = "sha1"
    elif args.sha512:
        algorithm = "sha512"
    else:
        algorithm = "sha256"

    # If --verify given with algorithm prefix, that wins
    if args.verify:
        detected_algo, expected_hex = parse_expected(args.verify)
        if detected_algo and not any([args.md5, args.sha1, args.sha512, args.sha256]):
            algorithm = detected_algo
        elif detected_algo is None and not any([args.md5, args.sha1, args.sha512, args.sha256]):
            # No algo prefix, no flag — try to infer from hex length
            inferred = detect_algo_from_hex(expected_hex)
            if inferred:
                algorithm = inferred
    else:
        expected_hex = None

    # Validate file
    if args.file != "-":
        p = Path(args.file)
        if not p.exists():
            print(f"hash-check: {args.file}: no such file", file=sys.stderr)
            sys.exit(2)
        if not p.is_file():
            print(f"hash-check: {args.file}: not a file", file=sys.stderr)
            sys.exit(2)

    try:
        digest = hash_file(args.file, algorithm)
    except OSError as e:
        print(f"hash-check: {e}", file=sys.stderr)
        sys.exit(2)

    # Verify mode
    if args.verify:
        match = digest.lower() == expected_hex.lower()
        if args.json:
            obj = {
                "file": args.file,
                "algorithm": algorithm,
                "digest": digest,
                "expected": expected_hex.lower(),
                "match": match,
            }
            print(json.dumps(obj, indent=2))
        elif not args.quiet:
            label = f"{algorithm.upper()}  {args.file}"
            status = "OK" if match else "MISMATCH"
            print(f"{status}  {label}")
            if not match:
                print(f"  expected: {expected_hex.lower()}", file=sys.stderr)
                print(f"  got:      {digest}", file=sys.stderr)
        sys.exit(0 if match else 1)
    else:
        # Plain compute mode
        if args.json:
            obj = {
                "file": args.file,
                "algorithm": algorithm,
                "digest": digest,
            }
            print(json.dumps(obj, indent=2))
        elif not args.quiet:
            print(f"{algorithm.upper()}  {digest}  {args.file}")


if __name__ == "__main__":
    main()
