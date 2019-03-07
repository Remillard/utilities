# Generates the output files for the project automatically at build end.
# Uses the Python program update_cof_filename to automatically version, date,
# time, and build stamp the file name.
proc call_update_cof_python {prefix suffix dir filename} {
	set output [exec python update_cof_filename.py -p $prefix -s $suffix -d $dir -b system_build_info_pkg.vhd $filename]
	puts $output
}

post_message "Executing generate_outputfiles.tcl script..."
post_message "=================================================================="
post_message "Generating output filenames in COF files..."
call_update_cof_python onx10k_fpga jic ../dev_firmware onx10k_fpga_jic.cof
post_message "=================================================================="

post_message "Generating JTAG Indirect Compressed Flash File (*.jic)..."
set cmd [exec quartus_cpf -c ../project/onx10k_fpga_jic.cof]
puts $cmd
post_message "=================================================================="
