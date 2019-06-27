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


def generate_mif(args, filename):
    """Creating a MIF formatted memory file based on the arguments."""
    # Max value is constrained to maximum positive value for 2's complement
    # numbers.
    depth = 2 ** args.depth
    if args.scale is not None:
        max_value = args.scale
    else:
        max_value = 2 ** (args.width - 1) - 1
    if args.rotation == "full":
        angle_step = 2 * math.pi / depth
    else:
        angle_step = 0.5 * math.pi / depth

    addr_nibbles = math.ceil(args.depth / 4)
    data_nibbles = math.ceil(args.width / 4)

    if args.function == "sin":
        func = math.sin
    else:
        func = math.cos

    lut_file = open(filename, "w")

    lut_file.write("DEPTH={}; % Memory Depth in Address Locations %\n".format(depth))
    lut_file.write("WIDTH={}; % Memory Width in Bits %\n".format(args.width))
    lut_file.write("ADDRESS_RADIX = HEX;\n")
    lut_file.write("DATA_RADIX = HEX;\n")
    lut_file.write("CONTENT\nBEGIN\n")

    # TODO: Support multiple values per line.
    for idx in range(0, depth):
        line = "{:0{size}X} : ".format(idx, size=addr_nibbles)
        angle = idx * angle_step
        value = round(max_value * func(angle))
        # Converte negative numbers to 16 bit 2's complement
        if value < 0:
            value = value + 2 ** args.width
        line = line + "{:0{size}X} ".format(value, size=data_nibbles)
        line = line + ";\n"
        lut_file.write(line)

    lut_file.write("END;\n")
    lut_file.close()


def generate_mem(args, filename):
    """Given a filename and parameters, generates the MEM formatted look up table."""
    # Max value is constrained to maximum positive value for 2's complement
    # numbers.
    depth = 2 ** args.depth
    if args.scale is not None:
        max_value = args.scale
    else:
        max_value = 2 ** (args.width - 1) - 1
    if args.rotation == "full":
        angle_step = 2 * math.pi / depth
    else:
        angle_step = 0.5 * math.pi / depth

    data_nibbles = math.ceil(args.width / 4)

    if args.function == "sin":
        func = math.sin
    else:
        func = math.cos

    lut_file = open(filename, "w")

    for idx in range(0, depth):
        line = ""
        angle = idx * angle_step
        value = round(max_value * func(angle))
        # Converte negative numbers to 16 bit 2's complement
        if value < 0:
            value = value + 2 ** args.width
        line = line + "{:0{size}X}\n".format(value, size=data_nibbles)
        lut_file.write(line)

    lut_file.close()


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
    parser.add_argument(
        "-d",
        "--depth",
        help="Memory depth specified in number of address bits.  Default: 12",
        default=12,
        type=int,
    )
    parser.add_argument(
        "-w",
        "--width",
        help="Data width specified in number of data bits.  Default: 16",
        default=16,
        type=int,
    )
    parser.add_argument(
        "-f",
        "--function",
        choices=["sin", "cos"],
        help="Function to be created.  Valid options are 'sin' and 'cos'.  Default: sin",
        default="sin",
    )
    parser.add_argument(
        "-s",
        "--scale",
        help="Full scale value.  Must be less than 2^(width-1)-1.  Default: 2^(width-1)-1",
        type=int,
    )
    parser.add_argument(
        "-r",
        "--rotation",
        choices=["full", "quad"],
        help="Rotational angle.  Valid options are 'full' and 'quad'.  Default: full",
        default="full",
    )
    parser.add_argument(
        "-fmt",
        "--format",
        choices=["mif", "mem"],
        help="Sets the output file format.  Default: mif",
        default="mif",
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
            scale_str = "scaled"
        depth = 2 ** args.depth
        filename = "{}_{}x{}_{}_{}_{}_lut.{}".format(
            args.prefix,
            args.width,
            depth,
            scale_str,
            args.rotation,
            args.function,
            args.format,
        )
        print("Generating {}".format(filename))

        if args.format == "mif":
            generate_mif(args, filename)
        else:
            generate_mem(args, filename)


if __name__ == "__main__":
    main()
