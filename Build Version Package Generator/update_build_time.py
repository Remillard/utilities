#! python3
'''
This script updates or generates entirely a VHDL file
containing information as constants about when the build
was executed.  This should be called as a precursor to
Quartus (or other tool) synthesizing the design.  In
Quartus, in the settings file, use:
set_global_assignment -name PRE_FLOW_SCRIPT_FILE
   "quartus_sh:python update_build_time.py"

The program will work with no command line arguments and the
default value is specified in PKG_FILENAME global.  However the
filename may be overridden using a commandline parameter '-o'.
'''

import os
import time
import re
import tempfile
import argparse

PKG_FILENAME = 'system_build_info_pkg.vhd'


def scanline(line):
    '''Scans a line for a number of predefined
    text strings and replaces if found.'''
    # Acquire the current time and setup some variables with
    # strings of the contents.
    longform_date = time.strftime('%c', time.localtime())
    year = time.strftime('%Y', time.localtime())
    month = time.strftime('%m', time.localtime())
    day = time.strftime('%d', time.localtime())
    hour = time.strftime('%H', time.localtime())
    minute = time.strftime('%M', time.localtime())
    second = time.strftime('%S', time.localtime())

    # Search for the following patterns and recreate the line if found.
    if re.search(r'-- Last update :', line):
        line = '-- Last update : {}\n'.format(longform_date)

    # Note, searching for the constant declaration line so users can
    # add vector conversions of these numbers safely without the lines
    # getting eaten.
    if re.search(r'constant C_BUILD_TIME_YEAR', line):
        line = '\tconstant C_BUILD_TIME_YEAR   : integer := {};\n'.format(year)

    if re.search(r'constant C_BUILD_TIME_MONTH', line):
        line = '\tconstant C_BUILD_TIME_MONTH  : integer := {};\n'.format(month)

    if re.search(r'constant C_BUILD_TIME_DAY', line):
        line = '\tconstant C_BUILD_TIME_DAY    : integer := {};\n'.format(day)

    if re.search(r'constant C_BUILD_TIME_HOUR', line):
        line = '\tconstant C_BUILD_TIME_HOUR   : integer := {};\n'.format(hour)

    if re.search(r'constant C_BUILD_TIME_MINUTE', line):
        line = '\tconstant C_BUILD_TIME_MINUTE : integer := {};\n'.format(minute)

    if re.search(r'constant C_BUILD_TIME_SECOND', line):
        line = '\tconstant C_BUILD_TIME_SECOND : integer := {};\n'.format(second)

    # This one is special as it searches for the constant, then increments
    # the number.
    if re.search(r'constant C_BUILD_NUMBER\b', line):
        s = re.search(r':= ([0-9]+);', line)
        build_num = int(s.group(1)) + 1
        print('Build number: {}'.format(build_num))
        line = '\tconstant C_BUILD_NUMBER : integer := {};\n'.format(build_num)

    return line

def update_file(filename):
    '''
    Opens the file and scans for fields, replacing them
    with the appropriate time information.
    '''
    longform_date = time.strftime('%c', time.localtime())
    print('=================================================================')
    print('Updating system build package with time: {}'.format(longform_date))
    # Open the original, and a temp file.  Not using contexts
    # because I want to control the file handling.
    f_in = open(filename, 'r')
    f_temp = tempfile.TemporaryFile(mode='r+')

    # Examine each line and write a potentially modified
    # version to the tempfile.
    for line in f_in:
        newline = scanline(line)
        f_temp.write(newline)

    # Close the read context on the file, and reopen as
    # write (overwriting.).  Rewind temp file.
    f_temp.seek(0)
    f_in.close()
    f_out = open(filename, 'w')

    # Rewrite the file from temporary contents.
    for line in f_temp:
        f_out.write(line)

    # Close all files.  Temp file will be destroyed.
    f_out.close()
    f_temp.close()
    print('Update complete')
    print('=================================================================')

def create_file(filename):
    '''
    Creates a file with the contents desired.  Uses a temp
    file and then scans it and writes it back into the real file
    because scanline was intended to work on a line by line basis.
    '''
    # This is the file contents to be written.
    package_str = '''-------------------------------------------------------------------------------
-- Title       : System Build Information Package
-------------------------------------------------------------------------------
-- File        : {}
-- Last update :
-------------------------------------------------------------------------------
-- Description:  This file is handled by the Python file
-- "update_build_time.py".  The commandline option -o specifies the file.  If
-- this file is not found at the path specified, it is created.  If it is
-- found, the time constants and build constant will be altered.
--
-- This file may be edited after creation with the following notes:
-- * The constant declarations for C_BUILD_<field> where 'field' is NUMBER,
--   YEAR, MONTH, DAY, HOUR, MINUTE, SECOND will be searched for on
--   subsequent executions of the program.  These should not be altered.
-- * The time and build fields may be used in other constants (for instance,
--   to convert to std_logic_vector).
-- * The C_BUILD_VERSION constants are not updated.  The *_STR is used by
--   the companion program 'update_cof_filename.py' to mark the output
--   filename.  C_BUILD_VERSION should be setup per project and then manually
--   modify the string version.  Build number can take the place of "many
--   releases" and release can be tied to formal release candidates.
-- * The C_BUILD_<time> will be updated with the time on each execution of the
--   program.
-- * The C_BUILD_NUMBER value will be incremented by one on each execution
--   of the program.
--
-- This program is intended to be run immediately before build.  In Quartus
-- this may be automated by the following field in the project *.qsf file
-- as follows:
-- set_global_assignment -name PRE_FLOW_SCRIPT_FILE
--        "quartus_sh:<TCL script that runs this program>"
-------------------------------------------------------------------------------
-- Revisions:  Revisions and commentary regarding such are controlled by
-- the revision control system in use (Rational Team Concert / Jazz).  That
-- tool should be consulted on revision history.
-------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package system_build_info is

\t----------------------------------------------------------------------
\t-- Firmware version.  C_BUILD_VERSION_STR is used by the post-build
\t-- script 'update_cof_filename.py' to create the output filename.
\t-- Setup C_BUILD_VERSION and C_BUILD_VERSION_SLV according to project
\t-- requirements.  Designer may put any other build defining constants
\t-- here safely as well.
\t----------------------------------------------------------------------
\tconstant C_BUILD_VERSION_STR : string := "1.0.0";
\tconstant C_BUILD_VERSION : integer := 1;
\tconstant C_BUILD_VERSION_SLV : std_logic_vector(15 downto 0) :=
\t\tstd_logic_vector(to_unsigned(C_BUILD_VERSION, 16));

\t----------------------------------------------------------------------
\t-- AUTOMATICALLY GENERATED AND UPDATED CONSTANTS
\t-- DO NOT EDIT THIS SECTION
\t----------------------------------------------------------------------
\tconstant C_BUILD_TIME_YEAR   : integer := 0;
\tconstant C_BUILD_TIME_MONTH  : integer := 0;
\tconstant C_BUILD_TIME_DAY    : integer := 0;
\tconstant C_BUILD_TIME_HOUR   : integer := 0;
\tconstant C_BUILD_TIME_MINUTE : integer := 0;
\tconstant C_BUILD_TIME_SECOND : integer := 0;

\tconstant C_BUILD_NUMBER : integer := 0;
\t----------------------------------------------------------------------
\t-- END OF AUTOMATICALLY UPDATED VALUES
\t-- Insert user code after this point.
\t----------------------------------------------------------------------

end package system_build_info;
'''.format(filename)

    longform_date = time.strftime('%c', time.localtime())
    print('=================================================================')
    print('Creating system build package with time: {}'.format(longform_date))

    f_temp = tempfile.TemporaryFile(mode='r+')
    f_temp.write(package_str)

    # Close the read context on the file, and reopen as
    # write (overwriting.).  Rewind temp file.
    f_temp.seek(0)
    f_out = open(filename, 'w')

    # Rewrite the file from temporary contents.
    for line in f_temp:
        newline = scanline(line)
        f_out.write(newline)

    # Close all files.  Temp file will be destroyed.
    f_out.close()
    f_temp.close()
    print('Creation complete')
    print('=================================================================')


def main():
    '''
    Main program.  Decides if the file exists already and if
    it needs to create the file entirely or just update fields
    '''
    # Setup ArgParse class
    parser = argparse.ArgumentParser(
        prog='update_build_time',
        description='''Creates or updates a VHDL package file
        that contains constants for date and time related to
        when this program was run.  update_build_time.py is
        intended to be run just prior to building the design.''')
    parser.add_argument(
        '-o', '--output_file',
        help='VHDL package output filename.  Default: {}'.format(PKG_FILENAME),
        default=PKG_FILENAME)
    args = parser.parse_args()

    # First check to see if the file exists.  Assuming that
    # we are properly keeping source files in a separate
    # directory from where the project is installed.
    if os.path.isfile(args.output_file):
        update_file(args.output_file)
    else:
        create_file(args.output_file)

if __name__ == '__main__':
    main()
