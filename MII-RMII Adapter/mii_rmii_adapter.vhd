--------------------------------------------------------------------------------
-- Title       : MII to RMII Interface Adapter
-- Project     : Utilities
--------------------------------------------------------------------------------
-- File        : mii_rmii_adapter.vhd
-- Author      : Mark Norton <mark.norton@viavisolutions.com>
-- Company     : Self
-- Created     : Fri Apr 19 09:00:54 2019
-- Last update : Fri Apr 19 15:37:56 2019
-- Platform    : Generic
-- Standard    : VHDL-2008
--------------------------------------------------------------------------------
-- Description: This is intended to bridge a MII FPGA output to RMII PHY.
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity mii_rmii_adapter is
	port (
		------------------------------------------------------------------------
		-- FPGA EMAC Side (MII format)
		------------------------------------------------------------------------
		mii_emac_clk_tx       : out std_logic;
		mii_emac_txd          : in  std_logic_vector(4 downto 0);
		mii_emac_txen         : in  std_logic;
		mii_emac_txer         : in  std_logic;
		mii_emac_rst_ckl_tx_n : in  std_logic;
		mii_emac_clk_rx       : out std_logic;
		mii_emac_rxd          : out std_logic_vector(4 downto 0);
		mii_emac_rxdv         : out std_logic;
		mii_emac_rxer         : out std_logic;
		mii_emac_rst_clk_rx_n : in  std_logic;
		mii_emac_speed        : in  std_logic_vector(1 downto 0);
		mii_emac_crs          : out std_logic;
		mii_emac_col          : out std_logic;
		------------------------------------------------------------------------
		-- PHY Side (RMII format)
		------------------------------------------------------------------------
		rmii_phy_ref_clk  : out std_logic;
		rmii_phy_txen     : out std_logic;
		rmii_phy_txd      : out std_logic_vector(1 downto 0);
		rmii_phy_rxdv_crs : in  std_logic;
		rmii_phy_rxd      : in  std_logic_vector(1 downto 0);
		rmii_phy_rxclk    : in  std_logic;
		rmii_phy_rxer     : in  std_logic
	);
end entity mii_rmii_adapter;
