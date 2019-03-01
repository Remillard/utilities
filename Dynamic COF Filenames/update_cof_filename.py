#! python 3
"""
This program reads in an Altera COF file.  This file contains data
related to converting the raw output of an FPGA build into a number of
different types.  What we'd like to do is dynamically update the
filename based on the version, build time, and build number.  This
information is generated at the beginning of the build time and stored in
the file system_build_info_pkg.vhd in the source directory.
"""
import os
import re
import argparse
import tempfile
from lxml import etree

SRC_FILE = "system_build_info_pkg.vhd"
OUTPUT_DIR = "../dev_firmware"
OUTPUT_FILENAME_PREFIX = "projectname"
OUTPUT_FILENAME_SUFFIX = "bin"


def parse_build_info(filename):
    """
    Method for reading the generated data out of the system build info
    source file.

    TODO: Make the searches more robust and permit failing operations
    (just in case).
    """
    with open(filename, "r") as f:
        for line in f:

            if re.search(r"constant C_BUILD_VERSION_STR\b", line):
                s = re.search(r':=\s*"([0-9_AB.]*)"', line)
                version = s.group(1)

            if re.search(r"constant C_BUILD_TIME_YEAR\b", line):
                s = re.search(r":= ([0-9]+);", line)
                year = s.group(1)

            if re.search(r"constant C_BUILD_TIME_MONTH\b", line):
                s = re.search(r":= ([0-9]+);", line)
                month = s.group(1)

            if re.search(r"constant C_BUILD_TIME_DAY\b", line):
                s = re.search(r":= ([0-9]+);", line)
                day = s.group(1)

            if re.search(r"constant C_BUILD_TIME_HOUR\b", line):
                s = re.search(r":= ([0-9]+);", line)
                hour = s.group(1)

            if re.search(r"constant C_BUILD_TIME_MINUTE\b", line):
                s = re.search(r":= ([0-9]+);", line)
                minute = s.group(1)

            if re.search(r"constant C_BUILD_TIME_SECOND\b", line):
                s = re.search(r":= ([0-9]+);", line)
                second = s.group(1)

            if re.search(r"constant C_BUILD_NUMBER\b", line):
                s = re.search(r":= ([0-9]+);", line)
                build = s.group(1)

    # Form string out of the various bits
    return "v{}_{}{}{}_{}{}{}_Build_{}".format(
        version, year, month, day, hour, minute, second, build
    )


def quote_hack(filename):
    """
    This is a method that corrects for a bug in the XML in Quartus.  The XML
    spec says that the strings in the XML declaration may be delimited by
    either single or double quotes.  Quartus's tool only supports double
    quotes.  lxml ElementTree only produces single quotes.  This method
    looks for the xml declaration and changes all single quotes on that line
    to double quotes.
    """
    f_in = open(filename, "r")
    f_temp = tempfile.TemporaryFile(mode="r+")
    for line in f_in:
        if re.search(r"<\?xml", line, re.I):
            line = re.sub("'", '"', line)
        f_temp.write(line)
    f_temp.seek(0)
    f_in.close()
    f_out = open(filename, "w")
    for line in f_temp:
        f_out.write(line)
    f_out.close()
    f_temp.close()


def main():
    """
    Main entry point for command line usage
    """
    # Parse the system build file and create the new filename.
    # Setup ArgParse class
    parser = argparse.ArgumentParser(
        prog="update_cof_filename",
        description="""Alters the 'output_filename' key in the Altera
        Convert Output File (*.cof) XML file to format the file with the
        build version, time, and build number prior to running the
        conversion.

        The filename created will be of the format:
            <filename prefix>_v<version>_<YYYYMMDD>_<HHMMSS>_<Build>
        """,
    )
    parser.add_argument(
        "cof_filename", help="The Altera COF file to alter.  Mandatory field."
    )
    parser.add_argument(
        "-p",
        "--prefix",
        help="The output filename prefix.  Default: {}".format(OUTPUT_FILENAME_PREFIX),
        default=OUTPUT_FILENAME_PREFIX,
    )
    parser.add_argument(
        "-s",
        "--suffix",
        help="The output filename suffix. (e.g. jic, rpd, rbf)",
        default=OUTPUT_FILENAME_SUFFIX,
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="The output filename directory.  Default: None",
        default="",
    )
    parser.add_argument(
        "-b",
        "--build_file",
        help="The system build package file.  Default: {}".format(SRC_FILE),
        default=SRC_FILE,
    )
    args = parser.parse_args()

    print("=================================================================")
    print("Reading {}".format(args.build_file))
    build_str = parse_build_info(args.build_file)
    new_filename = "{}_{}.{}".format(args.prefix, build_str, args.suffix)
    if args.directory:
        new_filename = args.directory + "/" + new_filename
    print("Updating {}".format(args.cof_filename))
    print("Output filename: {}".format(new_filename))
    cof_et = etree.parse(args.cof_filename)
    output_file = cof_et.find("output_filename")
    output_file.text = new_filename
    cof_et.write(
        args.cof_filename, xml_declaration=True, encoding="US-ASCII", standalone="yes"
    )
    quote_hack(args.cof_filename)
    print("Update complete.")
    print("=================================================================")


if __name__ == "__main__":
    main()
