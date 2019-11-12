--------------------------------------------------------------------------------
-- Title       : Generic Signal Generation Framework
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : generic_siggen.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Self
-- Created     : Thu Apr  4 13:13:52 2019
-- Last update : Tue Nov 12 09:03:17 2019
-- Platform    : Generic
-- Standard    : VHDL-2008
--------------------------------------------------------------------------------
-- Description: This is a starter structure for signal generation.  Due to
-- the way simulation works, you can never really get around the need to
-- create a time step, but if the work doing so is predone, putting user
-- generated signals into the framework should not be super difficult.
--
-- This is intended to run into the generic ADC model and then into a RTL
-- receiver.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
use std.textio.all;
use ieee.std_logic_textio.all;
use work.signals_pkg.all;
use work.signal_defs_pkg.all;

entity generic_siggen is
	port (
		signal_out : out real := 0.0
	);
end entity generic_siggen;

architecture behavioral of generic_siggen is
	----------------------------------------------------------------------------
	-- General Simulation Setup
	----------------------------------------------------------------------------
	-- The idea is to represent "real time" as closely as possible, however
	-- as noted, there's no way to get around time steps completely.  The
	-- smaller the time step, the closer to real time we can achieve, however
	-- the longer simulation will take.  Simulation resolution must be set to
	-- the step size or smaller.
	constant C_STEP_PS   : real := 10.0;
	constant C_TIME_STEP : time := C_STEP_PS * 1.0e-12 * (1 SEC);

	-- Simulation duration set here.  The signal generation block will be the
	-- controller of how long we last.
	constant C_SIM_DURATION : time := 50 us;

	-- Current time value as a real
	signal t : real := 0.0;

	----------------------------------------------------------------------------
	-- Signal Specific Constructs
	----------------------------------------------------------------------------
	-- CW signals and constants
	constant C_CW_FREQ   : real := 120.0e6; -- Hz
	constant C_CW_AMP    : real := 0.99;
	constant C_CW_OFFSET : real := 0.0;

	signal cw  : real := 0.0;
	signal phi : real := 0.0;

	-- PAM constructs
	constant C_OFF_VAL : real := 0.1;
	constant C_MAX_VAL : real := 1.0;
	signal m           : real := 0.0;

begin
	----------------------------------------------------------------------------
	-- Simulation Control
	----------------------------------------------------------------------------
	SIM_CONTROL : process
	begin
		wait for C_SIM_DURATION;
		std.env.stop(0);
		wait;
	end process SIM_CONTROL;

	----------------------------------------------------------------------------
	-- Time Control
	----------------------------------------------------------------------------
	TIME_CONTROL : process
	begin
		t <= t + C_STEP_PS * 1.0e-12;
		wait for C_TIME_STEP;
	end process TIME_CONTROL;

	----------------------------------------------------------------------------
	-- Signal Output -- Replace the signal_out linear with the result of the
	-- generated expression.
	----------------------------------------------------------------------------
	SIGNAL_OUTPUT : process
	begin
		signal_out <= m * cw + C_CW_OFFSET;
		wait for C_TIME_STEP;
	end process SIGNAL_OUTPUT;

	----------------------------------------------------------------------------
	-- User Generated Signals
	----------------------------------------------------------------------------
	-- Carrier Wave
	cw <= sinusoid(C_CW_AMP, C_CW_FREQ, 0.0, t);

	-- Modulation signal generation
	m <= piecewise(C_MODE_A_PATTERN, t);
	--m <= piecewise(C_MODE_C_PATTERN, t);
	--m <= piecewise(C_DME_X_PATTERN, t);

end architecture behavioral;
