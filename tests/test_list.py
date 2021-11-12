#!/usr/bin/env python3
#
# licensetool.py
#
# Copyright (c) 2021, Pelion Limited and affiliates.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Licensetool test cases for the list command argument."""

import os
import pandas as pd
import licensetool as t
from licensetool import _DATA_SHEET_NAME

# Test empty file
def test_empty_license():
    """Empty license file (fail)."""
    d_f, status = t.read_manifest_file("tests/empty_file.manifest")
    assert status["errors"] is True
    assert d_f.empty is True

# Test each of the lines (package, package version, recipe, license) missing
def test_no_line1():
    """Line1 (package) missing from manifest file (fail)."""
    d_f, status = t.read_manifest_file("tests/no-line1.manifest")
    assert status["errors"] is True
    assert d_f.empty is True

def test_no_line2():
    """Line2 missing from manifest file (fail)."""
    d_f, status = t.read_manifest_file("tests/no-line2.manifest")
    assert status["errors"] is True
    assert d_f.empty is True

def test_no_line3():
    """Line3 missing from manifest file (fail)."""
    d_f, status = t.read_manifest_file("tests/no-line3.manifest")
    assert status["errors"] is True
    assert d_f.empty is True

def test_no_line4():
    """Line4 missing from manifest file (fail)."""
    d_f, status = t.read_manifest_file("tests/no-line4.manifest")
    assert status["errors"] is True
    assert d_f.empty is True

def test_out_of_sync():
    """Out of sync error case in manifest file (fail)."""
    d_f, status = t.read_manifest_file("tests/out-of-sync.manifest")
    assert status["errors"] is True
    assert d_f.empty is False    # There will be one entry in the DataFrame

def test_broken_manifest():
    """Broken/malformatted manifest file (fail)."""
    d_f, status = t.read_manifest_file("tests/broken.manifest")
    assert status["errors"] is True
    assert d_f.empty is True

# Test a known successfull cases, with 3 packages only.
def test_3_packages():
    """Normal success case with 3 packages (success)"""
    d_f, status = t.read_manifest_file("tests/3-packages.manifest")
    assert status["errors"] is False
    assert status["lines"] == 16
    assert status["packages"] == 3
    assert d_f.empty is False
    ref_d_f = pd.read_csv("tests/3-packages.csv")
    assert d_f.equals(ref_d_f)

# Test a known successfull cases, with 3 packages only - via cli
# so that we can verify also the xlsx -version.
def test_3_packages_cli(tmpdir):
    """Normal success case with 3 packages via cli (success)"""
    # Also via cli for the Excel-version, too
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py list tests/3-packages.manifest " + tmp_outfile )
    assert ret == 0
    # Compare result, too
    ref_d_f = pd.read_csv("tests/3-packages.csv")
    result_d_f = pd.read_csv(tmp_outfile+".csv")
    assert result_d_f.equals(ref_d_f)
    # Also the Excel-version
    xl_result_d_f = pd.read_excel(tmp_outfile+".xlsx", sheet_name=_DATA_SHEET_NAME, engine='openpyxl')
    assert xl_result_d_f.equals(ref_d_f)

# No empty lines at the end eg. broken package
def test_3_packages_noemptylines():
    """Manifest file with no empty lines (malformatted) (fail)"""
    d_f, status = t.read_manifest_file("tests/3-packages.manifest.nolines")
    assert d_f.empty is False
    assert status["errors"] is True
