--------------------------------------------------------------------------------
-- Title       : Testbench for Receiver
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : rx_dsp_top_tb.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Self
-- Created     : Tue Nov 12 08:04:09 2019
-- Last update : Tue Nov 12 08:34:26 2019
-- Platform    : Generic
-- Standard    : VHDL-2008
--------------------------------------------------------------------------------
-- Description:
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all;

-----------------------------------------------------------

entity rx_dsp_top_tb is

end entity rx_dsp_top_tb;

-----------------------------------------------------------

architecture testbench of rx_dsp_top_tb is

	-- Testbench DUT generics


	-- Testbench DUT ports
	signal clk_160    : std_logic;
	signal reset      : std_logic;
	signal adc_data   : std_logic_vector(11 downto 0);
	signal phase_data : std_logic_vector(17 downto 0);
	signal mag_data   : std_logic_vector(17 downto 0);
	signal data_en    : std_logic;
	signal raw_iq     : std_logic_vector(31 downto 0);
	signal raw_iq_en  : std_logic;
	signal testpoints : std_logic_vector(63 downto 0);

	signal siggen_out : real;
	signal overrange  : std_logic;

	-- Other constants
	constant C_160MHZ_PERIOD : real := 6.25e-9; -- NS
	-- Simulation duration set here.  The signal generation block will be the
	-- controller of how long we last.
	constant C_SIM_DURATION : time := 50 us;


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

	-----------------------------------------------------------
	-- Clocks and Reset
	-----------------------------------------------------------
	CLK_160_GEN : process
	begin
		clk_160 <= '1';
		wait for C_160MHZ_PERIOD / 2.0 * (1 SEC);
		clk_160 <= '0';
		wait for C_160MHZ_PERIOD / 2.0 * (1 SEC);
	end process CLK_160_GEN;

	RESET_GEN : process
	begin
		reset <= '1',
			'0' after 20.0*C_160MHZ_PERIOD * (1 SEC);
		wait;
	end process RESET_GEN;

	-----------------------------------------------------------
	-- Testbench Stimulus
	-----------------------------------------------------------
	generic_siggen_1 : entity work.generic_siggen
		port map (
			signal_out => siggen_out
		);

	generic_adc_model_1 : entity work.generic_adc_model
		generic map (
			DATA_WIDTH     => 12,
			BIPOLAR        => true,
			VOLTAGE_SCALE  => 2.0,
			VOLTAGE_OFFSET => 0.0,
			TWOS_COMP      => true
		)
		port map (
			reset      => reset,
			analog_in  => siggen_out,
			sample_clk => clk_160,
			dout       => adc_data,
			overrange  => overrange
		);

	-----------------------------------------------------------
	-- Entity Under Test
	-----------------------------------------------------------
	DUT : entity work.rx_dsp_top
		port map (
			clk_160    => clk_160,
			reset      => reset,
			adc_data   => adc_data,
			phase_data => phase_data,
			mag_data   => mag_data,
			data_en    => data_en,
			raw_iq     => raw_iq,
			raw_iq_en  => raw_iq_en,
			testpoints => testpoints
		);

end architecture testbench;
