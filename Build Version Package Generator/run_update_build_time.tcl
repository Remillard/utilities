# Runs the Python update_build_time.py script to update the
# system build package.
proc call_python {} {
	set output [exec python ../bin/update_build_time.py -o ../src/system_build_info_pkg.vhd]
	post_message $output
}
post_message "Executing run_update_build_time.tcl script..."
post_message "================================================================="
post_message "Running system build update Python program"
call_python
post_message "================================================================="
