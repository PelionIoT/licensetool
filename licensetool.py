#!/usr/bin/env python3
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

"""A tool for dealing with Yocto license manifest files, converting them to CSV-format
or CSV-format with change information."""

import sys
import os
import logging
import argparse
import re
import tempfile
import pandas as pd

def _print_help():

    print("Yocto license manifest tool")
    print("")
    print("license-tool.py cvs --input <license manifest file> --output <CVS file> ")
    print("   Generate a CVS-formatted version of the Yocto manifest file")
    print("   For example license-tool.py cvs license.manifest licenses.cvs ")
    print("")
    print("license-tool.py changes --previous <manifest file> --current <manifest file> "
          "--output <CVS file>")
    print("   Generate a CVS-formatted version based on two Yocto manifest files that"
          " highlights the changes")
    print("   For example license-tool.py changes license.manifest.v83 license.manifest.v83 "
          "license-chanages.cvs")
    print("")
    print("Optional:")
    print(" --verbose   verbose output")
    print(" --debug     debug level output (warning, a lot!)")

# _get_file_size(file) - return size of file (name given as string) by seeking the end of file.
#
# NOTE! Does NOT check if file exists!
#
def _get_file_size(file):

    """Get file size by seeking it to the end."""
    with open(file, encoding="utf-8") as f_h:
        # Get file size so that we can recognize end of file reliably
        f_h.seek(0,2) # offset=0, whence = 2 at the end
        file_size = f_h.tell()  # position now at the end == file size
    return file_size

# read_manifest_file - read Yocto license manifest and turn into a Panda's dataframe
#                         and a status dictionary.
#
def read_manifest_file(input_file):

    """Read manifest file and return a Panda's dataframe ."""

    pattern = re.compile("PACKAGE NAME: (.*)\nPACKAGE VERSION: (.*)\nRECIPE NAME: (.*)\nLICENSE: (.*)\n\n")
    f_h = open(input_file, "r", encoding='utf8')
    data = f_h.read()
    # Create empty dataframe
    column_names = ["package", "version", "recipe", "license"]
    d_f = pd.DataFrame(columns=column_names)

    packageCount = 0
    errors = False
    prew = 0
    for info_field in re.finditer(pattern, data):
        packageCount+=1
        if info_field.span()[0] != prew:
            print("Invalid content in the file")
            errors = True # there is some content not matching the pattern in file.
        prew = info_field.span()[1]

        new_row = {column_names[0]: info_field.group(1),
                column_names[1]: info_field.group(2),
                column_names[2]: info_field.group(3),
                column_names[3]: info_field.group(4)}
        d_f = d_f.append(new_row, ignore_index=True)

    if packageCount == 0: # needs to have at least one package or it is an error
        print("Package count is zero")
        errors = True

    data_len = len(data)
    if data_len != prew:
        # if not all data was matched it is an error
        print("Invalid content at end of file")
        errors = True

    num_lines = sum(1 for line in data.split("\n"))
    status = {"lines": num_lines, "packages": packageCount, "errors": errors}
    return d_f, status

# _csv - generate CSV-file from a license manifest file
#           filenames of input file and output file needed as parameters
#
def _csv(inputfile, outputfile):

    logging.debug("_csv: '%s','%s'", inputfile, outputfile)

    # Covert the manifest to a Pandas dataframe
    d_f, status = read_manifest_file(inputfile)

    # Export CSV, if no errors noticed
    if status["errors"] is False:
        d_f.to_csv(outputfile, index=False)
    else:
        print("ERROR - could not process license manifest file " + inputfile)
        sys.exit(71) # EPROTO
    print(inputfile + " " + str(status) )

# _changes - generate change information based on two Yocto license manifest files
#
def _changes(previous, current, output):

    logging.debug("_changes: '%s', '%s', '%s'", previous, current, output)
    d_f_prev, status_prev = read_manifest_file(previous)
    if status_prev["errors"] is True:
        print("ERROR - handling of '" + previous + "' failed.")
        sys.exit(71) # EPROTO
    d_f_curr, status_curr = read_manifest_file(current)
    if status_curr["errors"] is True:
        print("ERROR - handling of '" + current + "' failed.")
        sys.exit(71) # EPROTO

    f_orig = tempfile.TemporaryFile()
    f_new = tempfile.TemporaryFile()
    #f_orig = open(output+"orig_csv.temp.csv", "w+")
    #f_new = open(output+"new_csv.temp.csv", "w+")

    output_file = open(output, "w", encoding="utf-8")
    d_f_prev.to_csv(f_orig, index=False)
    d_f_curr.to_csv(f_new, index=False)

    orig_csv = f_orig.readlines()
    new_csv = f_new.readlines()
    f_orig.close()
    f_new.close()

    first = True
    for line in new_csv:
        if line.strip():
            if line not in orig_csv:
                if first:
                    print("Changes in Modules (Not found in original eg. added or changes)")
                    first = False
                print(line.strip())
                output_file.write("new has,"+line)

    first = True
    for line in orig_csv:
        if line.strip():
            if line not in new_csv:
                if first:
                    print("\n")
                    print("Changes in Modules (Not found in new eg. removed or changes)")
                    first = False
                print(line.strip())
                output_file.write("old has,"+line)

def _parse_args():

    parser = argparse.ArgumentParser()

    # Two command modes, csv and change

    subparsers = parser.add_subparsers(dest="command")
    parser_csv = subparsers.add_parser("csv",
        help="create CVS file of Yocto License manifest file.")
    parser_csv.add_argument(
        "inputfile",
        help="Yocto license manifest file name (used as input)",
    )
    parser_csv.add_argument(
        "csvfile",
        help="Name for CSV-formatted output file name",
    )

    parser_changes = subparsers.add_parser("changes",
        help="Create changes highlighting list from two Yocto license manifest files.")
    parser_changes.add_argument(
        "previous",
        help="Previous Yocto license manifest file name",
    )
    parser_changes.add_argument(
        "current",
        help="Current Yocto license manifest file name",
    )
    parser_changes.add_argument(
        "changefile",
        help="Name for CSV-formatted changes file name",
    )

    parser.add_argument("--forcemode", help="Force overwrite of existing output", action='store_true')

    parser.add_argument("--verbose", help="Verbose diagnostics", action="store_const",
        dest="loglevel",const=logging.INFO)

    parser.add_argument("--debug", help="Extra diagnostic output", action="store_const",
        dest="loglevel",const=logging.DEBUG,default=logging.WARNING)

    args, unknown = parser.parse_known_args()

    logging.basicConfig(level=args.loglevel,format='')

    if not args.command:
        _print_help()
        sys.exit(0)

    if len(unknown) > 0:
        logging.error("unsupported arguments: %s ", str(unknown))
        sys.exit(8) # ENOEXEC
    return args

def main():

    """Script entry point."""
    args = _parse_args()
    if args.command == "csv":
        if not os.path.isfile(args.inputfile):
            print("ERROR - input file: '" + args.inputfile + "' does not exist.")
            sys.exit(2) # ENOENT
        if os.path.isfile(args.csvfile):
            if not args.forcemode:
                print("ERROR - output file: '" + args.csvfile + "' already exists.")
                sys.exit(2)  # ENOENT
            else:
                print("Warning - output file: '" + args.csvfile + "' already exists. Will overwrite")

        _csv(args.inputfile, args.csvfile)

    if args.command == "changes":
        if not os.path.isfile(args.previous):
            print("ERROR - previous license file: '" + args.previous + "' does not exist.")
            sys.exit(2) # ENOENT
        if not os.path.isfile(args.current):
            print("ERROR - current license file: '" + args.current + "' does not exist.")
            sys.exit(2) # ENOENT
        if os.path.isfile(args.changefile):
            if not args.forcemode:
                print("ERROR - output file: '" + args.changefile + "' already exists.")
                sys.exit(2)  # ENOENT
            else:
                print("Warning - output file: '" + args.changefile + "' already exists. Will overwrite")

        _changes(args.previous, args.current, args.changefile)

if __name__ == "__main__":

    sys.exit(main())
