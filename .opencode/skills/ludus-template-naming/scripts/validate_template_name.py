#!/usr/bin/env python3
"""Validate canonical Ludus template basenames and built names."""

from __future__ import annotations

import argparse
import re
import sys


LINUX_FAMILIES = {"ubuntu", "debian", "kali"}
ARCHITECTURES = {"x64", "arm64"}
LINUX_ROLES = {"desktop", "server"}
ALLOWED_NAME = re.compile(r"^[a-z0-9.-]+$")
NUMERIC_RELEASE = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")
WINDOWS_RELEASE = re.compile(r"^[0-9]+(?:\.[0-9]+)*(?:-[a-z0-9]*[a-z][a-z0-9]*)*$")
QUALIFIER = re.compile(r"^[a-z0-9]+$")
LOCALE = re.compile(r"^[a-z]{2}$")


def validate_name(name: str) -> str | None:
    if not name.isascii() or name != name.lower():
        return "lowercase ASCII"
    if not name or not ALLOWED_NAME.fullmatch(name):
        return "name must use lowercase ASCII letters, digits, dots, and hyphens"
    if any(separator in name for separator in ("--", "..")):
        return "repeated separator"

    suffix_count = name.count("-template")
    if suffix_count:
        if suffix_count != 1 or not name.endswith("-template"):
            return "-template is allowed only as one terminal suffix"
        name = name.removesuffix("-template")
        if "-template" in name:
            return "built name must contain exactly one terminal -template suffix"

    if re.fullmatch(r"flare-vm-[a-z]{2}", name):
        return None

    fields = name.split("-")
    if not fields or fields[0] not in LINUX_FAMILIES | {"windows"}:
        return "unknown OS family; expected ubuntu, debian, kali, windows, or windows-server"

    if fields[0] in LINUX_FAMILIES:
        if len(fields) < 5:
            return "expected Linux shape: <os>-<release>-<arch>-<role>[-<qualifier>...]-<locale>"
        release, arch, role = fields[1:4]
        qualifiers = fields[4:-1]
    elif len(fields) > 1 and fields[1] == "server":
        arch_index = next((index for index, field in enumerate(fields[2:], 2) if field in ARCHITECTURES), None)
        if arch_index is None or arch_index + 1 >= len(fields):
            return "expected Windows Server shape: windows-server-<release>-<arch>[-<qualifier>...]-<locale>"
        release = "-".join(fields[2:arch_index])
        arch = fields[arch_index]
        role = None
        qualifiers = fields[arch_index + 1 : -1]
    else:
        arch_index = next((index for index, field in enumerate(fields[1:], 1) if field in ARCHITECTURES), None)
        if arch_index is None or arch_index + 1 >= len(fields):
            return "expected Windows client shape: windows-<release>-<arch>[-<qualifier>...]-<locale>"
        release = "-".join(fields[1:arch_index])
        arch = fields[arch_index]
        role = None
        qualifiers = fields[arch_index + 1 : -1]

    if role is not None and role not in LINUX_ROLES:
        return "Linux role must be desktop or server"

    locale = fields[-1]
    if not LOCALE.fullmatch(locale):
        return "final locale must be two lowercase letters"
    release_pattern = NUMERIC_RELEASE if fields[0] in LINUX_FAMILIES else WINDOWS_RELEASE
    if not release_pattern.fullmatch(release):
        return "release must start with digits and use dots for numeric parts or hyphens for semantic alphanumeric parts"
    if arch not in ARCHITECTURES:
        return "architecture must be x64 or arm64"
    if any(not QUALIFIER.fullmatch(qualifier) for qualifier in qualifiers):
        return "qualifiers must use lowercase alphanumerics"
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate canonical Ludus template basenames and built names."
    )
    parser.add_argument("names", metavar="NAME", nargs="+")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = False
    for name in args.names:
        reason = validate_name(name)
        if reason is None:
            print(f"valid: {name}")
        else:
            print(f"invalid: {name}: {reason}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
