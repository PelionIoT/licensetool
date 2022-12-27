#!/bin/bash -ex
# ----------------------------------------------------------------------------
# Copyright 2021 Pelion
# Copyright 2021 Izuma Networks
#
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
# ----------------------------------------------------------------------------
set -ex

# Create virtual environment if one is not in place
if [[ ! -d venv ]]; then
    python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

if [[ $(pip show licensetool) ]]; then
    pip uninstall licensetool --yes
fi
pip install --editable .

pip install -r requirements.txt
pip install -r dev-requirements.txt
