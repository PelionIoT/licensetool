#!/usr/bin/env python3
#
# test_cli - test the command line interface (i.e. argument parsing)
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

def test_no_params():
    ret = os.system("python licensetool.py")
    assert ret == 0

def test_cvs_only():
    ret = os.system("python licensetool.py csv")
    assert ret != 0

def test_cvs_input_only():
    ret = os.system("python licensetool.py csv tests/3-packages.manifest")
    assert ret != 0

def test_cvs_input_output(tmpdir):
    tmp_outfile = str(tmpdir.join("out.cvs"))
    ret = os.system("python licensetool.py csv tests/3-packages.manifest " + tmp_outfile)
    assert ret == 0

def test_cvs_input_missing():
    ret = os.system("python licensetool.py csv non-existent-file tests/out.cvs")
    assert ret != 0

def test_cvs_output_existing():
    ret = os.system("python licensetool.py csv tests/3-packages.manifest tests/3-packages.manifest")
    assert ret != 0

def test_changes_only():
    ret = os.system("python licensetool.py changes")
    assert ret != 0

def test_changes_input1_missing():
    ret = os.system("python licensetool.py changes non-existent-file non-existent-file2 tests/out.cvs")
    assert ret != 0

def test_changes_input2_missing():
    ret = os.system("python licensetool.py changes tests/3-packages.manifest non-existent-file2 tests/out.cvs")
    assert ret != 0

def test_cvs_output_existing():
    ret = os.system("python licensetool.py changes tests/3-packages.manifest tests/3-packages.manifest.v2 tests/3-packages.manifest")
    assert ret != 0

def test_changes_input_ok_output(tmpdir):
    tmp_outfile = str(tmpdir.join("out.cvs"))
    ret = os.system("python licensetool.py changes tests/3-packages.manifest tests/3-packages.manifest.v2 " + tmp_outfile)
    assert ret == 0
