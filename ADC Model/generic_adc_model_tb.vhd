--------------------------------------------------------------------------------
-- Title       : Testbench for Generic ADC Model
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : generic_adc_model_tb.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Self
-- Created     : Thu Apr  4 11:10:34 2019
-- Last update : Thu Apr  4 11:29:18 2019
-- Platform    : Generic
-- Standard    : VHDL-2008
--------------------------------------------------------------------------------
-- Description:
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
use std.textio.all;
use ieee.std_logic_textio.all;

-----------------------------------------------------------

entity generic_adc_model_tb is

end entity generic_adc_model_tb;

-----------------------------------------------------------

architecture testbench of generic_adc_model_tb is

	-- Testbench DUT generics as constants
	constant DATA_WIDTH     : integer := 14;
	constant SAMPLE_FREQ    : integer := 100;

	-- Testbench DUT ports as signals
	signal reset      : std_logic;
	signal analog_in  : real := 0.0;
	signal sample_clk : std_logic;
	signal dout_1       : std_logic_vector(DATA_WIDTH-1 downto 0);
	signal dout_2       : std_logic_vector(DATA_WIDTH-1 downto 0);
	signal overrange_1  : std_logic;
	signal overrange_2  : std_logic;

	-- Other constants
	constant C_CLK_PERIOD : real := 10.0e-9; -- NS

begin
	-----------------------------------------------------------
	-- Clocks and Reset
	-----------------------------------------------------------
	CLK_GEN : process
	begin
		sample_clk <= '1';
		wait for C_CLK_PERIOD / 2.0 * (1 SEC);
		sample_clk <= '0';
		wait for C_CLK_PERIOD / 2.0 * (1 SEC);
	end process CLK_GEN;

	RESET_GEN : process
	begin
		reset <= '1',
		         '0' after 10.0*C_CLK_PERIOD * (1 SEC);
		wait;
	end process RESET_GEN;

	-----------------------------------------------------------
	-- Testbench Stimulus
	-----------------------------------------------------------
	STIMULUS : process
	begin
		analog_in <= 0.0;
		wait until reset = '0';

		analog_in <= 5.0;
		wait for 10 us;
		analog_in <= 4.5;
		wait for 10 us;
		analog_in <= 4.0;
		wait for 10 us;
		analog_in <= 3.5;
		wait for 10 us;
		analog_in <= 3.0;
		wait for 10 us;
		analog_in <= 2.5;
		wait for 10 us;
		analog_in <= 2.0;
		wait for 10 us;
		analog_in <= 1.5;
		wait for 10 us;
		analog_in <= 1.0;
		wait for 10 us;
		analog_in <= 0.5;
		wait for 10 us;
		analog_in <= 0.0;
		-- Overrange test
		wait for 10 us;
		analog_in <= -1.0;
		wait for 10 us;
		analog_in <= 2.5;
		wait for 10 us;
		analog_in <= 6.0;
		wait for 10 us;
		analog_in <= 2.5;

		wait for 10 us;
		std.env.stop(0);
		wait;
	end process STIMULUS;
	-----------------------------------------------------------
	-- Entity Under Test
	-----------------------------------------------------------
	DUT_1 : entity work.generic_adc_model
		generic map (
			DATA_WIDTH     => DATA_WIDTH,
			BIPOLAR        => true,
			VOLTAGE_SCALE  => 5.0,
			VOLTAGE_OFFSET => 2.5,
			SAMPLE_FREQ    => SAMPLE_FREQ,
			TWOS_COMP      => true
		)
		port map (
			reset      => reset,
			analog_in  => analog_in,
			sample_clk => sample_clk,
			dout       => dout_1,
			overrange  => overrange_1
		);

	DUT_2 : entity work.generic_adc_model
		generic map (
			DATA_WIDTH     => DATA_WIDTH,
			BIPOLAR        => false,
			VOLTAGE_SCALE  => 5.0,
			VOLTAGE_OFFSET => 0.0,
			SAMPLE_FREQ    => SAMPLE_FREQ,
			TWOS_COMP      => false
		)
		port map (
			reset      => reset,
			analog_in  => analog_in,
			sample_clk => sample_clk,
			dout       => dout_2,
			overrange  => overrange_2
		);

end architecture testbench;
