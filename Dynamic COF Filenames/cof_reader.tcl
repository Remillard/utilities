# Reads a COF file and extracts the output filename for later use.
proc read_cof {filename} \
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
	set dest_filename [string trimright $orig_dest_filename 4].sof
	puts $source_filename
	puts $dest_filename
}
