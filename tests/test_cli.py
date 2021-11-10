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

"""Licensetool test cases for the command line interface (CLI)."""

import os

def test_no_params():
    """Test with no parameters (success, print help)"""
    ret = os.system("python licensetool.py")
    assert ret == 0

def test_list_only():
    """Test with list argument only (fail)"""
    ret = os.system("python licensetool.py list")
    assert ret != 0

def test_list_non_valid_option():
    """Test with non-valid option (fail)"""
    ret = os.system("python licensetool.py list --nonvalidoption")
    assert ret != 0

def test_list_input_only():
    """Test with list and only input file (fail)"""
    ret = os.system("python licensetool.py list tests/3-packages.manifest")
    assert ret != 0

def test_list_input_output(tmpdir):
    """Test list with input and valid output (success)"""
    tmp_outfilebase = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py list tests/3-packages.manifest " + tmp_outfilebase)
    assert ret == 0

def test_list_input_missing(tmpdir):
    """Test list with non-existent input file (fail)"""
    tmp_outfilebase = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py list non-existent-file " + tmp_outfilebase)
    assert ret != 0

def test_list_broken_manifest(tmpdir):
    """Test list with broken input file (fail)"""
    tmp_outfilebase = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py list tests/broken.manifest " + tmp_outfilebase)
    assert ret != 0

def test_list_output_existing(tmpdir):
    """Test list with output file already existing (fail, don't overwrite)"""
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py list tests/3-packages.manifest " + tmp_outfile)
    # 1st time should pass.
    assert ret == 0
    # 2nd time must fail
    ret = os.system("python licensetool.py list tests/3-packages.manifest " + tmp_outfile)
    assert ret != 0

def test_list_forced_overwrite(tmpdir):
    """Test list with forced overwrite input and valid output (success)"""
    tmp_outfilebase = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py list tests/3-packages.manifest " + tmp_outfilebase)
    # This creates now out.csv and out.xlsx
    assert ret == 0
    # Now overwrite them
    ret = os.system("python licensetool.py --force list tests/3-packages.manifest "
     + tmp_outfilebase)
    assert ret == 0

def test_changes_only():
    """Test w changes option only (fail)"""
    ret = os.system("python licensetool.py changes")
    assert ret != 0

def test_changes_input2_missing():
    """Test w changes option and one input file only (fail)"""
    ret = os.system("python licensetool.py changes tests/3-packages.manifest ")
    assert ret != 0

def test_changes_output_missing():
    """Test w changes option and one input file only (fail)"""
    ret = os.system("python licensetool.py changes tests/3-packages.manifest "
                    "tests/3-packages.manifest.v2")
    assert ret != 0

def test_changes_input1_not_existing(tmpdir):
    """Test w changes option and non-existent input file (fail)"""
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py changes non-existent-file tests/3-packages.manifest.v2 "
                    + tmp_outfile)
    assert ret != 0

def test_changes_input2_not_existing(tmpdir):
    """Test w changes option and non-existent 2nd input file (fail)"""
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py changes tests/3-packages.manifest non-existent-file2 "
                    + tmp_outfile)
    assert ret != 0

def test_changes_unknown_option(tmpdir):
    """Test w changes option and unknown option (fail)"""
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py --unknownoption changes tests/3-packages.manifest "
                    "tests/3-packages.manifest.v2 " + tmp_outfile)
    assert ret != 0

def test_changes_input_ok_output(tmpdir):
    """Normal success case"""
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py changes tests/3-packages.manifest "
                    "tests/3-packages.manifest.v2 " + tmp_outfile)
    assert ret == 0


def test_changes_output_existing(tmpdir):
    """Output existing, will not overwrite (fail)"""
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py changes tests/3-packages.manifest "
                    "tests/3-packages.manifest.v2 " + tmp_outfile)
    # 1st time should pass.
    assert ret == 0
    # 2nd time must fail
    ret = os.system("python licensetool.py changes tests/3-packages.manifest "
                    "tests/3-packages.manifest.v2 " + tmp_outfile)
    assert ret != 0

def test_changes_forced_overwrite(tmpdir):
    """Output existing, forced overwrite (success)"""
    tmp_outfile = str(tmpdir.join("out"))
    ret = os.system("python licensetool.py changes tests/3-packages.manifest "
                    "tests/3-packages.manifest.v2 " + tmp_outfile)
    # This creates now out.csv and out.xlsx
    assert ret == 0
    # Now overwrite them
    ret = os.system("python licensetool.py --force changes "
                    "tests/3-packages.manifest tests/3-packages.manifest.v2 "
                     + tmp_outfile)
    assert ret == 0
