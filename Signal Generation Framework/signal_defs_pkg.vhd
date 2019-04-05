--------------------------------------------------------------------------------
-- Title       : Signal Definitions Package
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : signal_defs_pkg.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Self
-- Created     : Fri Apr  5 14:17:05 2019
-- Last update : Fri Apr  5 14:26:19 2019
-- Platform    : Generic
-- Standard    : VHDL-2008
--------------------------------------------------------------------------------
-- Description: Now that the signal generator is working, it'd be nice to
-- start making some known patterns.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all;
use work.signals_pkg.all;

package signal_defs_pkg is
	----------------------------------------------------------------------------
	-- Example Mode C Pattern
	----------------------------------------------------------------------------
	constant C_MODE_A_P1_START : real := 20.0e-6;
	constant C_MODE_A_P1_RISE  : real := C_MODE_A_P1_START + 0.075e-6;
	constant C_MODE_A_P1_FLAT  : real := C_MODE_A_P1_RISE + 0.8e-6;
	constant C_MODE_A_P1_FALL  : real := C_MODE_A_P1_FLAT + 0.075e-6;

	constant C_MODE_A_P3_START : real := C_MODE_A_P1_START + 8.0e-6;
	constant C_MODE_A_P3_RISE  : real := C_MODE_A_P3_START + 0.075e-6;
	constant C_MODE_A_P3_FLAT  : real := C_MODE_A_P3_RISE + 0.8e-6;
	constant C_MODE_A_P3_FALL  : real := C_MODE_A_P3_FLAT + 0.075e-6;

	constant C_MODE_A_P4_START : real := C_MODE_A_P3_START + 2.0e-6;
	constant C_MODE_A_P4_RISE  : real := C_MODE_A_P4_START + 0.075e-6;
	constant C_MODE_A_P4_FLAT  : real := C_MODE_A_P4_RISE + 0.8e-6;
	constant C_MODE_A_P4_FALL  : real := C_MODE_A_P4_FLAT + 0.075e-6;

	constant C_MODE_A_PATTERN : MULTI_FUNCTION_ARRAY :=
		(
			0  => (C_MODE_A_P1_START, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			1  => (C_MODE_A_P1_RISE, LINEAR, (0.1, 1.0, 0.0, 0.0, 0.0, 0.0)),
			2  => (C_MODE_A_P1_FLAT, VALUE, (1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
			3  => (C_MODE_A_P1_FALL, LINEAR, (1.0, 0.1, 0.0, 0.0, 0.0, 0.0)),
			4  => (C_MODE_A_P3_START, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			5  => (C_MODE_A_P3_RISE, LINEAR, (0.1, 1.0, 0.0, 0.0, 0.0, 0.0)),
			6  => (C_MODE_A_P3_FLAT, VALUE, (1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
			7  => (C_MODE_A_P3_FALL, LINEAR, (1.0, 0.1, 0.0, 0.0, 0.0, 0.0)),
			8  => (C_MODE_A_P4_START, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			9  => (C_MODE_A_P4_RISE, LINEAR, (0.1, 1.0, 0.0, 0.0, 0.0, 0.0)),
			10 => (C_MODE_A_P4_FLAT, VALUE, (1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
			11 => (C_MODE_A_P4_FALL, LINEAR, (1.0, 0.1, 0.0, 0.0, 0.0, 0.0)),
			12 => (C_MODE_A_P4_FALL + 20.0e-6, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			13 => (0.0, END_POINT, NULL_PARAMS)
		);

	----------------------------------------------------------------------------
	-- Example Mode C Pattern
	----------------------------------------------------------------------------
	constant C_MODE_C_P1_START : real := 20.0e-6;
	constant C_MODE_C_P1_RISE  : real := C_MODE_C_P1_START + 0.075e-6;
	constant C_MODE_C_P1_FLAT  : real := C_MODE_C_P1_RISE + 0.8e-6;
	constant C_MODE_C_P1_FALL  : real := C_MODE_C_P1_FLAT + 0.075e-6;

	constant C_MODE_C_P3_START : real := C_MODE_C_P1_START + 21.0e-6;
	constant C_MODE_C_P3_RISE  : real := C_MODE_C_P3_START + 0.075e-6;
	constant C_MODE_C_P3_FLAT  : real := C_MODE_C_P3_RISE + 0.8e-6;
	constant C_MODE_C_P3_FALL  : real := C_MODE_C_P3_FLAT + 0.075e-6;

	constant C_MODE_C_P4_START : real := C_MODE_C_P3_START + 2.0e-6;
	constant C_MODE_C_P4_RISE  : real := C_MODE_C_P4_START + 0.075e-6;
	constant C_MODE_C_P4_FLAT  : real := C_MODE_C_P4_RISE + 0.8e-6;
	constant C_MODE_C_P4_FALL  : real := C_MODE_C_P4_FLAT + 0.075e-6;

	constant C_MODE_C_PATTERN : MULTI_FUNCTION_ARRAY :=
		(
			0  => (C_MODE_C_P1_START, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			1  => (C_MODE_C_P1_RISE, LINEAR, (0.1, 1.0, 0.0, 0.0, 0.0, 0.0)),
			2  => (C_MODE_C_P1_FLAT, VALUE, (1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
			3  => (C_MODE_C_P1_FALL, LINEAR, (1.0, 0.1, 0.0, 0.0, 0.0, 0.0)),
			4  => (C_MODE_C_P3_START, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			5  => (C_MODE_C_P3_RISE, LINEAR, (0.1, 1.0, 0.0, 0.0, 0.0, 0.0)),
			6  => (C_MODE_C_P3_FLAT, VALUE, (1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
			7  => (C_MODE_C_P3_FALL, LINEAR, (1.0, 0.1, 0.0, 0.0, 0.0, 0.0)),
			8  => (C_MODE_C_P4_START, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			9  => (C_MODE_C_P4_RISE, LINEAR, (0.1, 1.0, 0.0, 0.0, 0.0, 0.0)),
			10 => (C_MODE_C_P4_FLAT, VALUE, (1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
			11 => (C_MODE_C_P4_FALL, LINEAR, (1.0, 0.1, 0.0, 0.0, 0.0, 0.0)),
			12 => (C_MODE_C_P4_FALL + 20.0e-6, VALUE, (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
			13 => (0.0, END_POINT, NULL_PARAMS)
		);


end package signal_defs_pkg;

package body signal_defs_pkg is

end package body signal_defs_pkg;
