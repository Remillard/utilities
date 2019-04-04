-------------------------------------------------------------------------------
-- Title       : System Build Information Package
-------------------------------------------------------------------------------
-- File        : system_build_info_pkg.vhd
-- Last update : Mon Mar  4 16:20:00 2019
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

	----------------------------------------------------------------------
	-- Firmware version.  C_BUILD_VERSION_STR is used by the post-build
	-- script 'update_cof_filename.py' to create the output filename.
	-- Setup C_BUILD_VERSION and C_BUILD_VERSION_SLV according to project
	-- requirements.  Designer may put any other build defining constants
	-- here safely as well.
	----------------------------------------------------------------------
	constant C_BUILD_VERSION_STR : string                        := "0.0.1";
	constant C_BUILD_VERSION_SLV : std_logic_vector(31 downto 0) := X"00000100";

	----------------------------------------------------------------------
	-- AUTOMATICALLY GENERATED AND UPDATED CONSTANTS
	-- DO NOT EDIT THIS SECTION
	----------------------------------------------------------------------
	constant C_BUILD_TIME_YEAR   : integer := 2019;
	constant C_BUILD_TIME_MONTH  : integer := 03;
	constant C_BUILD_TIME_DAY    : integer := 01;
	constant C_BUILD_TIME_HOUR   : integer := 14;
	constant C_BUILD_TIME_MINUTE : integer := 12;
	constant C_BUILD_TIME_SECOND : integer := 48;

	constant C_BUILD_NUMBER : integer := 457;
	----------------------------------------------------------------------
	-- END OF AUTOMATICALLY UPDATED VALUES
	-- Insert user code after this point.
	----------------------------------------------------------------------
	-- Creating versions that can be easily put into the HPS System.
	constant C_BUILD_DATE_SLV : std_logic_vector(31 downto 0) :=
		std_logic_vector(to_unsigned(C_BUILD_TIME_YEAR, 16)) &
		std_logic_vector(to_unsigned(C_BUILD_TIME_MONTH, 8)) &
		std_logic_vector(to_unsigned(C_BUILD_TIME_DAY, 8));

	constant C_BUILD_TIME_SLV : std_logic_vector(31 downto 0) :=
		std_logic_vector(to_unsigned(C_BUILD_TIME_HOUR, 16)) &
		std_logic_vector(to_unsigned(C_BUILD_TIME_MINUTE, 8)) &
		std_logic_vector(to_unsigned(C_BUILD_TIME_SECOND, 8));

	constant C_BUILD_NUMBER_SLV : std_logic_vector(31 downto 0) :=
		std_logic_vector(to_unsigned(C_BUILD_NUMBER, 32));

	constant C_SYSTEM_BUILD_SLV : std_logic_vector(127 downto 0) :=
		C_BUILD_VERSION_SLV &
		C_BUILD_DATE_SLV &
		C_BUILD_TIME_SLV &
		C_BUILD_NUMBER_SLV;

end package system_build_info;
