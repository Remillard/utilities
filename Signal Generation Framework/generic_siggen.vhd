--------------------------------------------------------------------------------
-- Title       : Generic Signal Generation Framework
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : generic_siggen.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Self
-- Created     : Thu Apr  4 13:13:52 2019
-- Last update : Thu Apr  4 17:02:15 2019
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
	constant C_STEP_PS   : real := 500.0;
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
	constant C_CW_AMP    : real := 1.0;
	constant C_CW_OFFSET : real := 0.0;

	signal cw  : real := 0.0;
	signal phi : real := 0.0;

	-- PAM constructs
	constant C_OFF_VAL : real := 0.1;
	constant C_MAX_VAL : real := 1.0;
	signal m           : real := 0.0;

	constant C_START    : real := 0.0;
	constant C_P1_ON_0  : real := C_START + 20.0e-6;
	constant C_P1_ON_1  : real := C_P1_ON_0 + 0.075e-6;
	constant C_P1_OFF_0 : real := C_P1_ON_1 + 0.8e-6;
	constant C_P1_OFF_1 : real := C_P1_OFF_0 + 0.075e-6;
	constant C_P3_ON_0  : real := C_P1_ON_0 + 21.0e-6;
	constant C_P3_ON_1  : real := C_P3_ON_0 + 0.075e-6;
	constant C_P3_OFF_0 : real := C_P3_ON_1 + 0.8e-6;
	constant C_P3_OFF_1 : real := C_P3_OFF_0 + 0.075e-6;
	constant C_P4_ON_0  : real := C_P3_ON_0 + 2.0e-6;
	constant C_P4_ON_1  : real := C_P4_ON_0 + 0.075e-6;
	constant C_P4_OFF_0 : real := C_P4_ON_1 + 1.6e-6;
	constant C_P4_OFF_1 : real := C_P4_OFF_0 + 0.075e-6;

	----------------------------------------------------------------------------
	-- Helper Functions
	----------------------------------------------------------------------------
	-- Used for piecewise linear functions.  Must specify the endpoints of the
	-- line.  The 1 parameter is the start, 2 is the end.  Input time must be
	-- within these two points
	function line
		(
			v1, t1, v2, t2 : real;
			t              : real
		) return real is
		variable slope : real;
	begin
		assert (t2 > t1)
			report "%%%% line function: time parameters non-increasing" severity ERROR;
		assert (t1 <= t and t <= t2)
			report "%%%% line function: time input " &
			real'image(t) &
			"not within point boundaries from " &
			real'image(t1) & " to " & real'image(t2)
			severity ERROR;
		slope := (v2 - v1) / (t2 - t1);
		return slope * (t - t1) + v1;
	end function line;

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
	-- Signal Output -- Replace the signal_out line with the result of the
	-- generated expression.
	----------------------------------------------------------------------------
	SIGNAL_OUTPUT : process
	begin
		signal_out <= m * cw;
		wait for C_TIME_STEP;
	end process SIGNAL_OUTPUT;

	----------------------------------------------------------------------------
	-- User Generated Signals
	----------------------------------------------------------------------------
	-- Carrier Wave
	cw <= C_CW_AMP * sin(2.0*math_pi*C_CW_FREQ*t + phi) + C_CW_OFFSET;

	-- PAM Signal -- Need a better abstraction model
	MODE_C : process (all)
	begin
		if (t >= C_START and t < C_P1_ON_0) then
			m <= C_OFF_VAL;
		elsif (t >= C_P1_ON_0 and t < C_P1_ON_1) then
			m <= line(C_OFF_VAL, C_P1_ON_0, C_MAX_VAL, C_P1_ON_1, t);
		elsif (t >= C_P1_ON_1 and t < C_P1_OFF_0) then
			m <= C_MAX_VAL;
		elsif (t >= C_P1_OFF_0 and t < C_P1_OFF_1) then
			m <= line(C_MAX_VAL, C_P1_OFF_0, C_OFF_VAL, C_P1_OFF_1, t);
		elsif (t >= C_P1_OFF_1 and t < C_P3_ON_0) then
			m <= C_OFF_VAL;
		elsif (t >= C_P3_ON_0 and t < C_P3_ON_1) then
			m <= line(C_OFF_VAL, C_P3_ON_0, C_MAX_VAL, C_P3_ON_1, t);
		elsif (t >= C_P3_ON_1 and t < C_P3_OFF_0) then
			m <= C_MAX_VAL;
		elsif (t >= C_P3_OFF_0 and t < C_P3_OFF_1) then
			m <= line(C_MAX_VAL, C_P3_OFF_0, C_OFF_VAL, C_P3_OFF_1, t);
		elsif (t >= C_P3_OFF_1 and t < C_P4_ON_0) then
			m <= C_OFF_VAL;
		elsif (t >= C_P4_ON_0 and t < C_P4_ON_1) then
			m <= line(C_OFF_VAL, C_P4_ON_0, C_MAX_VAL, C_P4_ON_1, t);
		elsif (t >= C_P4_ON_1 and t < C_P4_OFF_0) then
			m <= C_MAX_VAL;
		elsif (t >= C_P4_OFF_0 and t < C_P4_OFF_1) then
			m <= line(C_MAX_VAL, C_P4_OFF_0, C_OFF_VAL, C_P4_OFF_1, t);
		elsif (t >= C_P4_OFF_1) then
			m <= C_OFF_VAL;
		else
			m <= 0.0;
		end if;
	end process MODE_C;

end architecture behavioral;
