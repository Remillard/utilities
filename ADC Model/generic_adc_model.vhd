--------------------------------------------------------------------------------
-- Title       : Generic ADC Model
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : generic_adc_model.vhd
-- Author      : Mark Norton <remillard@gmail.com>
-- Company     : Self
-- Created     : Thu Apr  4 08:46:46 2019
-- Last update : Thu Apr  4 11:34:01 2019
-- Platform    : Behavioral Model
-- Standard    : VHDL-2008
-------------------------------------------------------------------------------
-- Description: This is a behavioral model of an analog-digital converter for
-- use with testing receiver chains in simulation.  This model does not try to
-- simulate various ADC physical implementation strategies.  This simply
-- creates a mathematical model for the ADC.  Intended to be used with
-- signal generation models producing real value output and then input to
-- RTL model of a receiver.
--
-- Generics:
-- DATA_WIDTH     : Integer.  Size of the output vector in bits.  Default 14.
-- BIPOLAR        : Boolean.  Declares whether input signal is scaled to
--                  VOLTAGE_OFFSET +- VOLTAGE_SCALE/2 (true) or VOLTAGE_OFFSET
--                  to VOLTAGE_OFFSET + VOLTAGE_SCALE (false).  Determines the
--                  limits when overrange error will trigger.  Default true.
-- VOLTAGE_SCALE  : Real.  Max swing of the input analog value.  Default 5V.
-- VOLTAGE_OFFSET : Real.  Sets voltage offset for input analog value.
--                  Default 0V.
-- SAMPLE_FREQ    : Integer.  Sampling frequency in MHz.  Default 100.
-- TWOS_COMP      : Boolean.  Determines data format to be signed or unsigned.
--                  Default true.
-------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
use std.textio.all;
use ieee.std_logic_textio.all;

entity generic_adc_model is
	generic (
		DATA_WIDTH     : integer := 14;
		BIPOLAR        : boolean := true;
		VOLTAGE_SCALE  : real    := 5.0;
		VOLTAGE_OFFSET : real    := 0.0;
		SAMPLE_FREQ    : integer := 100;
		TWOS_COMP      : boolean := true
	);
	port (
		reset     : in std_logic;
		analog_in : in real;

		sample_clk : in  std_logic;
		dout       : out std_logic_vector(DATA_WIDTH-1 downto 0);
		overrange  : out std_logic
	);
end entity generic_adc_model;

architecture behavioral of generic_adc_model is

	constant C_FULL_SCALE   : integer := 2**DATA_WIDTH;
	constant C_MAX_INT_VAL  : integer := 2**DATA_WIDTH - 1;
	constant C_HALF_INT_VAL : integer := 2**(DATA_WIDTH-1);

	signal top_value  : real    := 0.0;
	signal bot_value  : real    := 0.0;
	signal normalized : real    := 0.0;
	signal scaled     : real    := 0.0;
	signal rounded    : integer := 0;

	signal un_value : unsigned(DATA_WIDTH-1 downto 0) := (others => '0');
	signal sg_value : signed(DATA_WIDTH-1 downto 0)   := (others => '0');

begin
	----------------------------------------------------------------------------
	-- Input Conditioning / Scaling
	----------------------------------------------------------------------------
	-- Done as signals to account for the bipolar generic
	top_value <= VOLTAGE_OFFSET + VOLTAGE_SCALE / 2.0 when BIPOLAR else
		VOLTAGE_OFFSET + VOLTAGE_SCALE;
	bot_value <= VOLTAGE_OFFSET - VOLTAGE_SCALE / 2.0 when BIPOLAR else
		VOLTAGE_OFFSET;

	-- Clamped to prevent out of bound errors when assigning to unsigned and
	-- signed vectors.
	PROTECTED_CALC : process (all)
		variable norm : real := 0.0;
	begin
		norm := (analog_in - bot_value) / VOLTAGE_SCALE;
		if (norm > 1.0) then
			norm := 1.0;
		elsif (norm < 0.0) then
			norm := 0.0;
		end if;
		normalized <= norm;
	end process PROTECTED_CALC;

	scaled     <= normalized * real(C_MAX_INT_VAL);
	rounded    <= integer(scaled);

	un_value <= to_unsigned(rounded, DATA_WIDTH);
	sg_value <= to_signed(rounded - C_HALF_INT_VAL, DATA_WIDTH);

	----------------------------------------------------------------------------
	-- Data Sampling Operation
	----------------------------------------------------------------------------
	ADC_SAMPLING : process (sample_clk, reset)
	begin
		if (reset = '1') then
			dout <= (others => '0');
		elsif rising_edge(sample_clk) then
			if (BIPOLAR) then
				dout <= std_logic_vector(sg_value);
			else
				dout <= std_logic_vector(un_value);
			end if;
		end if;
	end process ADC_SAMPLING;

	----------------------------------------------------------------------------
	-- Overrange Check
	----------------------------------------------------------------------------
	OVERRANGE_CHECK : process (analog_in)
	begin
		if (analog_in > top_value or analog_in < bot_value) then
			overrange <= '1';
		else
			overrange <= '0';
		end if;
		assert (overrange = '0')
			report "%%%% OVERRANGE INPUT DETECTED" severity WARNING;
	end process OVERRANGE_CHECK;

end architecture behavioral;
