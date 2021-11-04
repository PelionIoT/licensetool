#!/usr/bin/env python3
#
# licensetool.py / test_changes.py
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

import os
import pytest
import pandas as pd
import licensetool as t

# Test previous empty file
def test_empty_license_prev(tmpdir):
    tmp_outfile = str(tmpdir.join("out.cvs"))
    ret = os.system("python licensetool.py changes tests/empty_file.manifest tests/3-packages.manifest.v2 " + tmp_outfile)
    assert ret != 0

# Test empty current file
def test_empty_license_curr(tmpdir):
    tmp_outfile = str(tmpdir.join("out.cvs"))
    ret = os.system("python licensetool.py changes tests/3-packages.manifest tests/empty_file.manifest " + tmp_outfile)
    assert ret != 0

# If output file exists, it should refuse to overwrite
def test_outfile_exists(tmpdir):
    ret = os.system("python licensetool.py changes tests/3-packages.manifest tests/3-packages.manifest tests/empty_file.manifest")
    assert ret != 0

# Invalid previous
def test_invalid_previous(tmpdir):
    ret = os.system("python licensetool.py changes tests/broken.manifest tests/3-packages.manifest tests/empty_file.manifest")
    assert ret != 0

# Invalid current
def test_invalid_current(tmpdir):
    ret = os.system("python licensetool.py changes tests/3-packages.manifest tests/broken.manifest tests/empty_file.manifest")
    assert ret != 0

# Success case
def test_changes_3packages_v2(tmpdir):
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py changes tests/3-packages.manifest tests/3-packages.manifest.v2 " + tmp_outfile )
    assert ret == 0

# Success case
def test_changes_v1_v2(tmpdir):
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py changes tests/changes-test.v1 tests/changes-test.v2 " + tmp_outfile )
    assert ret == 0
    # Compare result, too
    ref_df = pd.read_csv("tests/test-changes.csv")
    result_df = pd.read_csv(tmp_outfile+".csv")
    assert result_df.equals(ref_df)
    # Also the Excel-version
    xl_result_df = pd.read_excel(tmp_outfile+".xlsx",  engine='openpyxl')
    assert xl_result_df.equals(ref_df)
