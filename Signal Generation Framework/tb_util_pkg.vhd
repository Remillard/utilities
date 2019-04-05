--------------------------------------------------------------------------------
-- Title       : Testbench Utility Package
-- Project     : ONX-10k FPGA
--------------------------------------------------------------------------------
-- File        : tb_util_pkg.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Viavi Solutions
-- Created     : Thu Nov 29 09:09:50 2018
-- Last update : Fri Apr  5 14:20:41 2019
-- Platform    : Intel Arria 10 SX
-- Standard    : VHDL-2008
--------------------------------------------------------------------------------
-- Copyright (c) 2018 Viavi Solutions
--
-- This document contains controlled technology or technical data under the
-- jurisdiction of the Export Administration Regulations (EAR), 15 CFR 730-774.
-- It cannot be transferred to any foreign third party without the specific
-- prior approval of the U.S. Department of Commerce Bureau of Industry and
-- Security (BIS). Violations of these regulations are punishable by fine,
-- imprisonment, or both.
--------------------------------------------------------------------------------
-- Description: This is a package containing general utilitarian procedures for
-- testbenches.
--------------------------------------------------------------------------------
-- Revisions:  Revisions and commentary regarding such are controlled by
-- the revision control system in use (Rational Team Concert / Jazz).  That
-- tool should be consulted on revision history.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all;

package tb_util_pkg is
	----------------------------------------------------------------------------
	-- Shorthand message output with variable output selection (the output
	-- stream) and parameter to toggle output if desired.  Requires a string
	-- input.  Will not work with a line type.
	----------------------------------------------------------------------------
	file dbg_stream : TEXT open WRITE_MODE is "STD_OUTPUT";

	procedure write_note
		(
			file out_stream :    text;
			value           : in string;
			debug           : in boolean := TRUE
		);

end package tb_util_pkg;

package body tb_util_pkg is
	----------------------------------------------------------------------------
	-- Shorthand message output with variable output selection (the output
	-- stream) and parameter to toggle output if desired.
	----------------------------------------------------------------------------
	procedure write_note
		(
			file out_stream :    text;
			value           : in string;
			debug           : in boolean := TRUE
		) is
		variable L : line;
	begin
		if (debug) then
			write(L, string'("%% NOTE : @Time : "));
			write(L, now, RIGHT, 15);
			write(L, string'(" : "));
			write(L, value);
			writeline(out_stream, L);
		end if;
	end procedure write_note;

end package body tb_util_pkg;
