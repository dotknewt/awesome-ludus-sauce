#!/usr/bin/env python3
"""Regression tests for canonical Ludus template identifiers."""

import unittest

from validate_template_name import validate_name


class ValidateTemplateNameTest(unittest.TestCase):
    def test_accepts_canonical_windows_semantic_release_and_flare_names(self):
        for name in (
            "windows-11-22h2-x64-enterprise-no",
            "windows-11-22h2-x64-enterprise-no-template",
            "windows-server-2019-x64-no-security-updates-no",
            "flare-vm-no",
            "flare-vm-no-template",
        ):
            self.assertIsNone(validate_name(name), name)

    def test_rejects_legacy_underscore_names(self):
        self.assertIsNotNone(validate_name("windows-11_22h2-x64-enterprise-no"))


if __name__ == "__main__":
    unittest.main()
