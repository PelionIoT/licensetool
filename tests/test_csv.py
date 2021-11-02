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

import pytest
import pandas as pd
import licensetool as t

# Test empty file
def test_empty_license():
    df, status = t.read_manifest_file("tests/empty_file.manifest")
    assert status["errors"] == True
    assert df.empty == True

# Test each of the lines (package, package version, recipe, license) missing
def test_no_line1():
    df, status = t.read_manifest_file("tests/no-line1.manifest")
    assert status["errors"] == True
    assert df.empty == True

def test_no_line2():
    df, status = t.read_manifest_file("tests/no-line2.manifest")
    assert status["errors"] == True
    assert df.empty == True

def test_no_line3():
    df, status = t.read_manifest_file("tests/no-line3.manifest")
    assert status["errors"] == True
    assert df.empty == True

def test_no_line4():
    df, status = t.read_manifest_file("tests/no-line4.manifest")
    assert status["errors"] == True
    assert df.empty == True

def test_out_of_sync():
    df, status = t.read_manifest_file("tests/out-of-sync.manifest")
    assert status["errors"] == True
    assert df.empty == False    # There will be one entry in the DataFrame

def test_broken_manifest():
    df, status = t.read_manifest_file("tests/broken.manifest")
    assert status["errors"] == True
    assert df.empty == True

# Test a known successfull cases, with 3 packages only.
def test_3_packages():
    df, status = t.read_manifest_file("tests/3-packages.manifest")
    assert status["errors"] == False
    assert status["lines"] == 16
    assert status["packages"] == 3
    assert df.empty == False
    ref_df = pd.read_csv("tests/3-packages.csv")
    assert df.equals(ref_df)

# No empty lines at the end eg. broken package
def test_3_packages_noemptylines():
    df, status = t.read_manifest_file("tests/3-packages.manifest.nolines")
    assert status["errors"] == True