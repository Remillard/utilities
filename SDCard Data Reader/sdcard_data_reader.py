#! python 3
"""
Module receives a CSV table from the Logic Analyzer with the following columns:
clock, cmd, data (hex nibble).  The program scans through each line looking for
the start of a command or a response and prints it out.
"""
import argparse
import csv
from enum import Enum, auto
from bitvector import BitVector


class States(Enum):
    """Finite State Machine Enumeration"""

    idle = auto()
    acquire = auto()


def main():
    """Initial entry point.  Command line parameters."""
    parser = argparse.ArgumentParser(
        prog="sdcard_data_reader",
        description="""Reads commands from a serial data stream and decodes.""",
    )
    parser.add_argument("input_file", help="Input CSV filename.  Required.")
    parser.add_argument(
        "-s",
        "--sample_rate",
        help="Sample rate in nanoseconds.  Default = 10.",
        default=10,
    )
    args = parser.parse_args()

    print("Reading from : {}".format(args.input_file))

    with open(args.input_file) as csvfile:
        sddata = csv.DictReader(csvfile)
        # print("Field Names: {}".format(sddata.fieldnames))

        # Initialize state machine
        current_state = States.idle

        last_clk = 0
        last_cmd = 1
        current_cmd_idx = 0
        # DictReader skips the first line for field names and indexing line
        # numbers at 1 means the first data line is line # 2
        line_count = 2
        last_clk_edge_line = 0
        last_freq = 0
        for row in sddata:
            clk = int(row["clk"])
            cmd = int(row["cmd"])
            data = int(row["data"], 16)
            # print("Line Count: {} Clk: {} Cmd: {} Data: {}".format(line_count, clk, cmd, data))

            # Identify edges
            rising_edge_clk = False
            falling_edge_clk = False
            rising_edge_cmd = False
            falling_edge_cmd = False
            if clk == 1 and last_clk == 0:
                rising_edge_clk = True
            elif clk == 0 and last_clk == 1:
                falling_edge_clk = True
            if cmd == 1 and last_cmd == 0:
                rising_edge_cmd = True
            elif cmd == 0 and last_cmd == 1:
                falling_edge_cmd = True

            # Try to calculate clock rate
            if rising_edge_clk:
                edge_to_edge = line_count - last_clk_edge_line
                #print("Line Count: {} Last: {} E2E: {} Rate: {}".format(line_count, last_clk_edge_line, edge_to_edge, args.sample_rate))
                clock_freq = 1.0 / (float(edge_to_edge) * float(args.sample_rate) * float(1e-9))
                #print("Transaction Clock Rate: {} Hz".format(clock_freq))
                last_clk_edge_line = line_count

            # if rising_edge_clk: print("Line: {}  Rising Edge Clk Found".format(line_count))
            # if falling_edge_clk: print("Line: {}  Falling Edge Clk Found".format(line_count))
            # if rising_edge_cmd: print("Line: {}  Rising Edge Cmd Found".format(line_count))
            # if falling_edge_cmd: print("Line: {}  Falling Edge Cmd Found".format(line_count))

            if current_state == States.idle:
                # When not in a sequence, we watch for the falling edge of the
                # CMD line to indicate the start of a TX/RX transaction.
                bit_count = 0
                if falling_edge_cmd:
                    vector = BitVector()
                    current_state = States.acquire
                    if clock_freq != last_freq:
                        print("Transaction Clock Rate: {} Hz".format(clock_freq))
                        last_freq = clock_freq

            elif current_state == States.acquire:
                # Once a transaction begins, we'll always clock data in on the
                # rising edge of the clock.  This did not work for slow sample
                # rates because the host transitions data on a rising edge, but
                # with sufficiently fast sampling, the clock precedes the next
                # data bit.  At the faster clock rate the slew between clock and
                # data is such that we still want always rising edge.
                if rising_edge_clk:
                    vector.append(cmd)
                    bit_count += 1

                # End of transaction is defined by the number of bits.  Usually
                # 48 bits, however if the prior transaction was a command type
                # 2, 9, or 10, the number of bits is 136.
                if current_cmd_idx in (2, 9, 10):
                    max_bit = 136
                else:
                    max_bit = 48

                if bit_count == max_bit:
                    # End of transaction.  Branch between command and response
                    # types.
                    start_txrx = vector.slice(vector.length - 1, vector.length - 2)

                    if start_txrx.value == 1:
                        # Command
                        cmd_idx = vector.slice(45, 40)
                        argument = vector.slice(39, 8)
                        crc7_stop = vector.slice(7, 0)
                        if current_cmd_idx != 55:
                            print(
                                "Command:      Raw: {:012x}  Start + Tx: {:02x}  Cmd Idx:  CMD{:02d}  Arg: {:08x}  CRC7 + Stop: {:02x}".format(
                                    vector.value,
                                    start_txrx.value,
                                    cmd_idx.value,
                                    argument.value,
                                    crc7_stop.value,
                                )
                            )
                        else:
                            print(
                                "Command:      Raw: {:012x}  Start + Tx: {:02x}  Cmd Idx: ACMD{:02d}  Arg: {:08x}  CRC7 + Stop: {:02x}".format(
                                    vector.value,
                                    start_txrx.value,
                                    cmd_idx.value,
                                    argument.value,
                                    crc7_stop.value,
                                )
                            )
                        current_cmd_idx = cmd_idx.value

                    else:
                        # Response
                        if max_bit != 136:
                            # R1, R3, R6 Response
                            cmd_idx = vector.slice(45, 40)
                            argument = vector.slice(39, 8)
                            crc7_stop = vector.slice(7, 0)
                            if cmd_idx.value == 63:
                                print(
                                    "R3 (OCR):     Raw: {:012x}  Start + Rx: {:02x}  Reserved:    {:02x}  OCR: {:08x}  Reserved:    {:02x}".format(
                                        vector.value,
                                        start_txrx.value,
                                        cmd_idx.value,
                                        argument.value,
                                        crc7_stop.value,
                                    )
                                )
                            elif cmd_idx.value == 3:
                                new_rca = vector.slice(39, 24)
                                card_status = vector.slice(23, 8)
                                print(
                                    "R6 (RCA):     Raw: {:012x}\n              Start Rx: {:02x}\n              Cmd Idx:  {:02x}\n              RCA: {:04x}\n              Card Status: {:04x}\n              CRC7 Stop: {:02x}".format(
                                        vector.value,
                                        start_txrx.value,
                                        cmd_idx.value,
                                        new_rca.value,
                                        card_status.value,
                                        crc7_stop.value,
                                    )
                                )
                            else:
                                print(
                                    "R1 (Normal):  Raw: {:012x}  Start + Rx: {:02x}  Cmd Idx:  CMD{:02d}  Arg: {:08x}  CRC7 + Stop: {:02x}".format(
                                        vector.value,
                                        start_txrx.value,
                                        cmd_idx.value,
                                        argument.value,
                                        crc7_stop.value,
                                    )
                                )
                        else:
                            # R2 Response
                            start_tx = vector.slice(135, 134)
                            cmd_idx = vector.slice(133, 128)
                            cid_csr = vector.slice(127, 0)
                            print(
                                "R2 (CID/CSR): Raw: {:034x}\n              Start Rx: {:02x}\n              Reserved: {:02x}\n              CID/CSR + Stop: {:032x}".format(
                                    vector.value,
                                    start_tx.value,
                                    cmd_idx.value,
                                    cid_csr.value,
                                )
                            )
                            current_cmd_idx = 0

                    # Return to the idle state
                    current_state = States.idle

            line_count += 1
            last_clk = clk
            last_cmd = cmd


if __name__ == "__main__":
    main()
