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
import pandas as pd

# Yocto license file headers/row identifiers
PACK_NAME = "PACKAGE NAME:"
PACK_VER  = "PACKAGE VERSION:"
REC_NAME  = "RECIPE NAME:"
LIC_NAME  = "LICENSE:"

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

    """Read license manifest file and turn into a DataFrame."""
    # File format is:
    # PACKAGE NAME: acl
    # PACKAGE VERSION: 2.2.53
    # RECIPE NAME: acl
    # LICENSE: GPLv2+
    # empty line
    # - next similar entry
    logging.debug("_read_manifest_file: %s",input_file)

    file_size = _get_file_size(input_file)
    with open(input_file, encoding="utf-8") as f_h:

        # Create empty dataframe
        column_names = ["package", "version", "recipe", "license"]
        d_f = pd.DataFrame(columns = column_names)

        lines_left = True
        lines = 0
        packages = 0
        problems = False
        while lines_left is True:
            line1 = f_h.readline()
            lines = lines + 1
            if line1.find(PACK_NAME) == 0:
                # Pack name found
                logging.debug("line1='%s'", line1.strip())
            else:
                if line1 in ('', '\r\n', '\n') and lines != 0 : # empty line, likely ends here
                    logging.debug("line1 is empty")
                    lines_left = False
                    problems = True
                else:
                    # could be we are at the end, two empty lines there
                    posnow = f_h.tell()
                    if posnow >= (file_size - 2):
                        logging.debug("Within 2 chars of file end %s,  EOF reached.", str(posnow))
                    else:
                        problems = True
                        logging.error("Error - line {lines} has no {PACK_NAME}")
                        lines_left = False
                    break
            line2 = f_h.readline()
            lines = lines + 1
            if line2.find(PACK_VER) == 0:
                # Pack version found
                logging.debug("line2='%s'", line2.strip() )
            else:
                lines_left = False
                problems = True
                logging.error("Error - line %s has no %s", str(lines), PACK_VER)
                break
            line3 = f_h.readline()
            lines = lines + 1
            if line3.find(REC_NAME) == 0:
                # Recipe name found
                logging.debug("line3='%s'", line3.strip())
            else:
                lines_left = False
                problems = True
                logging.error("Error - line %s has no %s", str(lines), REC_NAME)
                break
            line4 = f_h.readline()
            lines = lines + 1
            if line4.find(LIC_NAME) == 0:
                # License name found
                logging.debug("line4='%s'", line4.strip())
            else:
                lines_left = False
                problems = True
                logging.error("Error - line %s has no %s", str(lines), LIC_NAME)
                break
            line5 = f_h.readline()
            lines = lines + 1
            if line5 in ("\n", "\r\n", "\n\r"):
                # OK, empty line found
                logging.debug("line5 is empty")
            else:
                if line5 == "": # nothing, end of file
                    lines_left = False
                else:
                    # Out of sync somehow?
                    logging.error("ERROR - OUT OF SYNC at %s expecting empty line"
                                  ", got %s",  str(lines), line5)
                    problems = True
                    lines_left = False
            # We have a package to add
            new_row = {column_names[0] : line1[len(PACK_NAME)+1:len(line1)-1],
                    column_names[1] : line2[len(PACK_VER) +1:len(line2)-1],
                    column_names[2] : line3[len(REC_NAME) +1:len(line3)-1],
                    column_names[3] : line4[len(LIC_NAME) +1:len(line4)-1] }
            logging.info(str(new_row))
            #append row to the dataframe
            d_f = d_f.append(new_row, ignore_index = True)
            packages = packages + 1

            # Check next line to see if it's empty too (likely end of file then
            # it ends with 2 empty lines)
            posnow = f_h.tell()
            nextline = f_h.readline()
            # 2nd empty line in row, file ends?
            if nextline in ("\n", "\r\n", "\n\r") and posnow >= (file_size - 2):
                logging.debug("Empty line, end reached at %s/%s.", str(posnow), str(file_size))
                lines = lines + 1
                lines_left = False
            else:
                # it's not empty line, let's get back where we were and process next entry
                f_h.seek(posnow)

    # All done or some error encountered.
    if problems is True:
        dbgstr = "Processed " + str(lines) + " lines and " + str(packages) + \
                 " packages, but with errors."
        logging.info(dbgstr)
    else:
        dbgstr = "Processed " + str(lines) + " lines and " + str(packages) + \
                 " packages successfully."
        logging.info(dbgstr)
    status = {"lines": lines, "packages": packages, "errors" : problems}
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
    # Merge the tables
    d_f = d_f_prev.compare(d_f_curr, align_axis=1, keep_shape=True, keep_equal=True )
    # Loop through for changes
    # Export CSV
    d_f.to_csv(output, index=False)
    print(current + " " + str(status_prev) )
    print(previous + " " + str(status_curr) )

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
            print("ERROR - output file: '" + args.csvfile + "' already exists.")
            sys.exit(1) # EPERM
        _csv(args.inputfile, args.csvfile)

    if args.command == "changes":
        if not os.path.isfile(args.previous):
            print("ERROR - previous license file: '" + args.previous + "' does not exist.")
            sys.exit(2) # ENOENT
        if not os.path.isfile(args.current):
            print("ERROR - current license file: '" + args.current + "' does not exist.")
            sys.exit(2) # ENOENT
        if os.path.isfile(args.changefile):
            print("ERROR - output file: '" + args.changefile + "' already exists.")
            sys.exit(1) # EPERM
        _changes(args.previous, args.current, args.changefile)

if __name__ == "__main__":

    sys.exit(main())
