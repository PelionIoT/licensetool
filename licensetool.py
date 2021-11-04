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

# read_manifest_file - read Yocto license manifest and turn into a Panda's dataframe
#                         and a status dictionary.
#
def read_manifest_file(input_file):

    """Read manifest file and return a Panda's dataframe ."""

    pattern = re.compile("PACKAGE NAME: (.*)\nPACKAGE VERSION: (.*)\nRECIPE NAME: (.*)\n"
                         "LICENSE: (.*)\n\n")
    with open(input_file, "r", encoding='utf8') as f_h:
        data = f_h.read()
        # Create empty dataframe
        column_names = ["package", "version", "recipe", "license"]
        d_f = pd.DataFrame(columns=column_names)

        package_count = 0
        errors = False
        prew = 0
        for info_field in re.finditer(pattern, data):
            package_count+=1
            if info_field.span()[0] != prew:
                print("ERROR - Invalid content in the file, got " + str(package_count)
                      + " packages.")
                errors = True # there is some content not matching the pattern in file.
            prew = info_field.span()[1]

            new_row = {column_names[0]: info_field.group(1),
                    column_names[1]: info_field.group(2),
                    column_names[2]: info_field.group(3),
                    column_names[3]: info_field.group(4)}
            d_f = d_f.append(new_row, ignore_index=True)

        if package_count == 0: # needs to have at least one package or it is an error
            print("Package count is zero")
            errors = True

        data_len = len(data)
        if data_len != prew:
            # if not all data was matched it is an error
            print("ERROR - Invalid content at end of file, got " + str(package_count)
                   + " packages.")
            errors = True

        num_lines = sum(1 for line in data.split("\n"))
        status = {"lines": num_lines, "packages": package_count, "errors": errors}
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
    d_f_prev.rename(
        columns={"version":"prev_ver", "license":"prev_license", "recipe":"prev_recipe"},
        inplace=True
    )
    if status_prev["errors"] is True:
        print("ERROR - handling of '" + previous + "' failed.")
        sys.exit(71) # EPROTO

    d_f_curr, status_curr = read_manifest_file(current)
    d_f_curr.rename(
        columns={"version":"curr_ver", "license":"curr_license", "recipe":"curr_recipe"},
        inplace=True
    )
    if status_curr["errors"] is True:
        print("ERROR - handling of '" + current + "' failed.")
        sys.exit(71) # EPROTO



    # 1st create a merged table that has both previous and current information
    d_f_combo = pd.merge(d_f_prev, d_f_curr, on = "package", how = "outer")
    logging.debug(d_f_combo)

    # With that, we can now start going it through and add the "changes" columns
    # to highlight what has changed.
    # Not going to consider recipe change a change worth high-lighting, that is not relevant from
    # Third Party IP point of view.

    d_f_combo[["change", "version_change","license_change","package_change"]] = "n"
    i = 0
    rows = d_f_combo.shape[0]
    styled = d_f_combo.style
    while i < rows:
        # Check package appearing, start by setting change is "n"
        package_change = False
        if pd.isna(d_f_combo.at[i, "prev_recipe"]): # NaN
            d_f_combo.at[i, "change"] = "y"
            d_f_combo.at[i, "package_change"] = "new package"
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("curr_recipe"), color="yellow", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("package"), color="yellow", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("curr_ver"), color="yellow", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("curr_license"), color="yellow", axis=None)
            package_change = True
        # Package removed
        if package_change is False and pd.isna(d_f_combo.at[i, "curr_recipe"]): # NaN
            d_f_combo.at[i, "change"] = "y"
            d_f_combo.at[i, "package_change"] = "dropped package"
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("prev_recipe"), color="yellow", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("prev_ver"), color="yellow", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("package"), color="yellow", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("prev_license"), color="yellow", axis=None)

            package_change = True
        # Version change
        if package_change is False and d_f_combo.at[i, "prev_ver"] != d_f_combo.at[i, "curr_ver"]:
            d_f_combo.at[i, "change"] = "y"
            d_f_combo.at[i, "version_change"] = "y"

            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("prev_ver"), color="lightgreen", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("curr_ver"), color="lightgreen", axis=None)
        # License change
        if package_change is False and \
           d_f_combo.at[i, "prev_license"] != d_f_combo.at[i, "curr_license"]:
            d_f_combo.at[i, "change"] = "y"
            d_f_combo.at[i, "license_change"] = "y"
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("prev_license"), color="red", axis=None)
            styled = styled.apply(style_single_cell, row=i, colum=d_f_combo.columns.get_loc("curr_license"), color="red", axis=None)
        # No changes cases is the default, as we set all change columns to n at start
        i = i + 1
    # Export result out
    d_f_combo.to_csv(output, index=False)

    #add autofilters to excel sheet
    writer = pd.ExcelWriter(output+".xlsx", engine='openpyxl')
    styled.to_excel(writer, sheet_name='Sheet1', index=False)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    ws = workbook.active
    ws.auto_filter.ref = ws.dimensions
    writer.save()
    #styled.to_excel(output+".xlsx", engine='openpyxl', index=False)


def style_single_cell(x, row, colum, color):
    new_color = 'background-color:  %s' % color
    df1 = pd.DataFrame('', index=x.index, columns=x.columns)
    df1.iloc[row, colum] = new_color
    return df1


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
    parser.add_argument("--force",
        help="Force overwrite of existing output file",
        action='store_true'
    )
    parser.add_argument("--verbose",
        help="Verbose diagnostics",
        action="store_const",
        dest="loglevel",
        const=logging.INFO
    )
    parser.add_argument("--debug",
        help="Extra diagnostic output",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING
    )
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
            if not args.force:
                print("ERROR - output file: '" + args.csvfile + "' already exists.")
                sys.exit(2)  # ENOENT
            else:
                print("Warning - output file: '" + args.csvfile + "' already exists. "
                    "Will overwrite.")

        _csv(args.inputfile, args.csvfile)

    if args.command == "changes":
        if not os.path.isfile(args.previous):
            print("ERROR - previous license file: '" + args.previous + "' does not exist.")
            sys.exit(2) # ENOENT
        if not os.path.isfile(args.current):
            print("ERROR - current license file: '" + args.current + "' does not exist.")
            sys.exit(2) # ENOENT
        if os.path.isfile(args.changefile):
            if not args.force:
                print("ERROR - output file: '" + args.changefile + "' already exists.")
                sys.exit(2)  # ENOENT
            else:
                print("Warning - output file: '" + args.changefile + "' already exists. "
                    "Will overwrite.")

        _changes(args.previous, args.current, args.changefile)

if __name__ == "__main__":

    sys.exit(main())
