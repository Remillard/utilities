--------------------------------------------------------------------------------
-- Title       : Signal Generation Package
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : signals_pkg.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Self
-- Created     : Fri Apr  5 08:19:13 2019
-- Last update : Fri Apr  5 14:20:41 2019
-- Platform    : Generic
-- Standard    : VHDL-2008
--------------------------------------------------------------------------------
-- Description: Trying to abstract some things in the generic signal generation
-- framework file.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
use std.textio.all;
use ieee.std_logic_textio.all;
use work.tb_util_pkg.all;

package signals_pkg is
	function const_val (val, t : real) return real;

	function linear (v1, t1, v2, t2, t : real) return real;

	function sinusoid (amp, freq, phi, t : real) return real;

	function gaussian (amp, sigma, center, tscale, t : real) return real;

	-- This only works because I'm only using reals for parameters.
	type REAL_PARAMS is record
		p1, p2, p3, p4, p5, p6 : real;
	end record;
	constant NULL_PARAMS : REAL_PARAMS := (others => 0.0);

	type PW_FUNCTIONS is (VALUE, LINEAR, GAUSSIAN, SINUSOID, END_POINT);
	type FUNCTION_ENTRY is record
		end_time    : real;
		pw_function : PW_FUNCTIONS;
		params      : REAL_PARAMS;
	end record;

	type MULTI_FUNCTION_ARRAY is array (natural range <>) of FUNCTION_ENTRY;

	function piecewise
		(
			func_array : MULTI_FUNCTION_ARRAY;
			t          : real
		) return real;

end package signals_pkg;

package body signals_pkg is
	----------------------------------------------------------------------------
	-- Linear function as defined by two points
	-- Parameters:
	--   v1, t1 : Start point of the line
	--   v2, t2 : End point of the line
	--   t      : Current time function input.
	----------------------------------------------------------------------------
	function linear (v1, t1, v2, t2, t : real) return real is
		variable slope : real;
	begin
		assert (t2 > t1)
			report "%%%% line function: time parameters non-increasing" severity ERROR;
		assert (t1 <= t and t <= t2)
			report "%%%% line function: time input " & real'image(t) & "not within point boundaries from " & real'image(t1) & " to " & real'image(t2) severity ERROR;
		slope := (v2 - v1) / (t2 - t1);
		return slope * (t - t1) + v1;
	end function linear;

	-- This is a degenerate version of linear made for convenience.
	function const_val (val, t : real) return real is
	begin
		return val;
	end function const_val;

	----------------------------------------------------------------------------
	-- Sinusoid function
	-- Parameters:
	--   amp    : Amplitude of the sinusoid centered around 0
	--   freq   : Frequency of the sinusoid in Hz.
	--   phi    : Phase offset of the sinusoid in radians.
	--   t      : Current time function input.
	----------------------------------------------------------------------------
	function sinusoid (amp, freq, phi, t : real) return real is
	begin
		return amp * sin(2.0*math_pi*freq*t + phi);
	end function sinusoid;

	----------------------------------------------------------------------------
	-- Gaussian function
	-- Parameters:
	--   amp    : The function will normalize the center point to 1.0.  This
	--            parameter will scale it to the desired voltage level.
	--   sigma  : The standard distribution sigma for the gaussian.  Controls
	--            the spread of the shape.
	--   center : The center point in seconds as a real of the shape.
	--   tscale : The gaussian formula is based around numbers on the scale of
	--            natural numbers.  This is intended to create very small
	--            timescale versions.  This value is used along with center
	--            and t to scale things up to natural numbers.  For example if
	--            the general time base for the shape is microseconds, set this
	--            value to 1.0e-6, then use sigma to control the shape.
	--   t      : Current time function input.
	----------------------------------------------------------------------------
	function gaussian (amp, sigma, center, tscale, t : real) return real is
		variable vscale      : real;
		variable scaled_time : real;
	begin
		-- Calculate scaling factor
		vscale := math_sqrt_2 * math_sqrt_pi * sigma;
		-- Calculate the scaled up time value
		scaled_time := (t - center) / tscale;
		-- Calculate scaled gaussian shape
		return amp * vscale * (1.0 / (math_sqrt_2 * math_sqrt_pi * sigma)) * math_e ** (-scaled_time**2 / (2.0 * sigma**2));
	end function gaussian;

	----------------------------------------------------------------------------
	-- Piecewise function
	-- Designed to let the user put together a number of function patterns
	-- covering various time periods and this function sorts out which time
	-- zone we're in and runs the proper function.
	----------------------------------------------------------------------------
	function piecewise
		(
			func_array : MULTI_FUNCTION_ARRAY;
			t          : real
		) return real is
		variable i          : natural := 0;
		variable start_time : real    := 0.0;
		variable rval : real := 0.0;
		variable L : line;
	begin
		ARRAY_SCAN : loop
			if (func_array(i).pw_function = END_POINT) then
				rval := func_array(i).params.p1;
				exit;
			elsif (t > func_array(i).end_time) then
				start_time := func_array(i).end_time;
				i          := i + 1;
			else
				case (func_array(i).pw_function) is
					when VALUE =>
						rval := const_val(func_array(i).params.p1, t);
						exit;
					when LINEAR =>
						rval := linear(func_array(i).params.p1, start_time, func_array(i).params.p2, func_array(i).end_time, t);
						exit;
					when GAUSSIAN =>
						rval := gaussian(func_array(i).params.p1, func_array(i).params.p2, func_array(i).params.p3, func_array(i).params.p4, t);
						exit;
					when SINUSOID =>
						rval := sinusoid(func_array(i).params.p1, func_array(i).params.p2, func_array(i).params.p3, t);
						exit;
					when others =>
						assert (FALSE) report "%%%% Invalid piecewise function name" severity FAILURE;
						exit;
				end case;
			end if;
		end loop ARRAY_SCAN;
		return rval;
	end function piecewise;

end package body signals_pkg;
