# Generates the output files for the project automatically at build end.
# Uses the Python program update_cof_filename to automatically version, date,
# time, and build stamp the file name.
proc call_update_cof_python {prefix suffix dir filename} {
	set output [exec python ../bin/update_cof_filename.py -p $prefix -s $suffix -d $dir -b ../src/system_build_info_pkg.vhd $filename]
	post_message $output
}

proc copy_sof_file {filename} \
{
	set infile [open $filename r]
	while { [gets $infile line] >= 0 } {
		if { [regexp {<output_filename>(.*?)</output_filename>} $line fullmatch group1] > 0 } {
			set orig_dest_filename $group1
		}
		if { [regexp {<sof_filename>(.*?)</sof_filename>} $line fullmatch group1] > 0 } {
			set source_filename $group1
		}
	}
	close $infile
	# Putting these post_message strings here because it's known at this point
	set strlen [string length $orig_dest_filename]
	set strbase [string range $orig_dest_filename 0 [expr $strlen - 5]]
	set dest_filename ${strbase}.sof
	#post_message "Filename: $strbase"
	post_message "Copying STAPL Object File (*.sof)..."
	file copy -force $source_filename $dest_filename
	return $strbase
}

post_message "Executing generate_outputfiles.tcl script..."
post_message "================================================================="
post_message "Generating output filenames in COF files..."
call_update_cof_python onx10k_fpga jic ../dev_firmware onx10k_fpga_jic.cof
#call_update_cof_python onx10k_fpga rbf ../dev_firmware onx10k_fpga_crbf.cof
#post_message "================================================================="
set filebase [copy_sof_file onx10k_fpga_jic.cof]
post_message "Generating JTAG Indirect Compressed Flash File (*.jic)..."
set cmd [exec quartus_cpf -c ../project/onx10k_fpga_jic.cof]
puts $cmd
post_message "Renaming automatically generated RPD file..."
file rename -force ${filebase}_auto.rpd ${filebase}.rpd
#post_message "Generating Compressed Raw Binary Format File (*.rbf)..."
#set cmd [exec quartus_cpf -c ../project/onx10k_fpga_crbf.cof]
#puts $cmd
post_message "================================================================="
