#! python 3
"""
This tool generates a sinusoidal look-up table memory initialization file for
use with block ROM in FPGA design.  There are a number of command line
parameters for sinusoid type (cos/sin), size, full vs. quarter and so forth.
With the proper option, it will also generate in 'mem' format which is useful
for simulation.
"""
import argparse
import math


def generate_file(args, filename):
    """Creating a MIF formatted memory file based on the arguments."""
    # Max value is constrained to maximum positive value for 2's complement
    # numbers.
    if args.scale is not None:
        max_value = args.scale
    else:
        max_value = 2 ** (args.datawidth - 1) - 1

    # TODO Actually support the num samples option!
    # Adding the endpoint means we need to squeeze both the origin and end in,
    # which means we need to shorten the angle step by one address.
    depth = 2 ** args.addrwidth
    if args.endpoint:
        num_samples = depth - 1
    else:
        num_sample = depth

    if args.rotation == "full":
        angle_step = 2 * math.pi / num_samples
    elif args.rotation == "quad":
        angle_step = 0.5 * math.pi / num_samples
    elif args.rotation == "eighth":
        angle_step = 0.25 * math.pi / num_samples

    addr_nibbles = math.ceil(args.addrwidth / 4)
    data_nibbles = math.ceil(args.datawidth / 4)

    if args.function == "sin":
        func = math.sin
    else:
        func = math.cos

    lut_file = open(filename, "w")

    if args.format == "mif":
        write_mif_header(lut_file, depth, args.datawidth)
    elif args.format == "mem":
        write_mem_header(lut_file, depth, args.datawidth)

    # TODO: Support multiple values per line.
    for idx in range(0, depth):
        angle = idx * angle_step
        value = round(max_value * func(angle))
        # Converte negative numbers to 16 bit 2's complement
        if value < 0:
            value = value + 2 ** args.datawidth

        if args.format == "mif":
            write_mif_line(lut_file, idx, addr_nibbles, value, data_nibbles)
        elif args.format == "mem":
            write_mem_line(lut_file, value, data_nibbles)

    if args.format == "mif":
        write_mif_footer(lut_file)

    lut_file.close()


def write_mif_header(lut_file, depth, datawidth):
    """Specific header to MIF file formats."""
    lut_file.write(f"DEPTH={depth}; % Memory Depth in Address Locations %\n")
    lut_file.write(f"WIDTH={datawidth}; % Memory Width in Bits %\n")
    lut_file.write("ADDRESS_RADIX = HEX;\n")
    lut_file.write("DATA_RADIX = HEX;\n")
    lut_file.write("CONTENT\nBEGIN\n")


def write_mif_line(lut_file, address, addr_nibbles, data, data_nibbles):
    line = f"{address:0{addr_nibbles}X} : {data:0{data_nibbles}X} ;\n"
    lut_file.write(line)


def write_mif_footer(lut_file):
    lut_file.write("END;\n")


def write_mem_header(lut_file, depth, datawidth):
    """Specific header to Verilog MEM file format."""
    lut_file.write("// Verilog Hex Memory Format\n")
    lut_file.write(f"// DEPTH={depth}\n")
    lut_file.write(f"// WIDTH={datawidth}\n")
    lut_file.write("// DATA_RADIX = HEX\n")


def write_mem_line(lut_file, data, data_nibbles):
    line = f"{data:0{data_nibbles}X}\n"
    lut_file.write(line)


def main():
    """Main entry point for program."""
    parser = argparse.ArgumentParser(
        prog="generate_lut",
        description="""Creates a memory initialization file for a sinusoid.""",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        help="MIF output filename prefix.  Default: 'rom'",
        default="rom",
    )
    mem_depth_group = parser.add_mutually_exclusive_group()
    mem_depth_group.add_argument(
        "-aw",
        "--addrwidth",
        help="""Memory depth specified in the width of the address.  The number
        of samples will be 2 ^ addrwidth.  Mutually exclusive option with number
        of samples.  Default: 12""",
        default=12,
        type=int,
    )
    mem_depth_group.add_argument(
        "-ns",
        "--numsamples",
        help="""Memory depth specified in number of look up table samples.  The
        number of address bits will be calculated to be 2 ^ ceiling(log2(numsamples)).
        Address values not covered will be set to 0.  Mutually exclusive option
        with depth.  Default: 4096""",
        default=12,
        type=int,
    )
    parser.add_argument(
        "-dw",
        "--datawidth",
        help="Data width specified in number of data bits.  Default: 16",
        default=16,
        type=int,
    )
    parser.add_argument(
        "-f",
        "--function",
        choices=["sin", "cos"],
        help="""Function to be created.  Valid options are 'sin' and 'cos'.
        Default: sin""",
        default="sin",
    )
    parser.add_argument(
        "-s",
        "--scale",
        help="""Full scale value.  Must be less than 2^(datawidth-1)-1.
        Default: 2^(datawidth-1)-1""",
        type=int,
    )
    parser.add_argument(
        "-r",
        "--rotation",
        choices=["full", "quad", "eighth"],
        help="""Rotational angle.  Valid options are 'full' and 'quad' and
        'eighth'.  Note that the eighth mode does not automatically generate
        both sin/cos outputs but that's how it's intended to be done, so run
        the program again to generate the other function.  Default: full""",
        default="full",
    )
    parser.add_argument(
        "-fmt",
        "--format",
        choices=["mif", "mem"],
        help="""Sets the output file format.  MIF is the Intel Memory
        Initialization File format (similar to MTI as well).  MEM is the
        Verilog Hex Memory format.  Default: mif""",
        default="mif",
    )
    parser.add_argument(
        "-ep",
        "--endpoint",
        action="store_true",
        help="""This option adjusts the address to angle ratio slightly by
        altering the angle step per address to include the endpoint.  Normally
        the sweep will run [sin(0), sin(2*pi)).  This is primarily useful for
        the quarter and eighth options.  For example with an eighth rotation
        sine sweep and 12 address bits, 16 data bits, the value at 0xfff will
        be (2^15 - 1) * sin(pi/4) = 0x5a82.  Care may need to be taken with the
        angle determination.  Default: Do not include the endpoint."""
    )
    # TODO: Add other RADIX arguments someday instead of just HEX.
    args = parser.parse_args()

    # Error check for full scale value.  args.scale equivalent to None is
    # fine, however if specified, must not be greater than the maximum
    # possible value.
    if args.scale is not None and args.scale > 2 ** (args.width - 1) - 1:
        print(
            "Argument Error: Full scale value must be less than or equal to the maximum possible.  A signed number at {} bits has a maximum scale value of {}.".format(
                args.width, 2 ** (args.width - 1) - 1
            )
        )
    else:
        # Construct filename
        if args.scale is None:
            scale_str = ""
        else:
            scale_str = "scaled_"

        # TODO: Actually support the number of samples option
        if args.addrwidth:
            depth = 2 ** args.addrwidth
        else:
            print("Error: Nonbinary depth not yet supported despite the fact it's in the help text.")

        filename = "{}_{}x{}_{}{}_{}_lut.{}".format(
            args.prefix,
            args.datawidth,
            depth,
            scale_str,
            args.rotation,
            args.function,
            args.format,
        )
        print("Generating {}".format(filename))

        generate_file(args, filename)


if __name__ == "__main__":
    main()
