#!/bin/bash

# compare 2 sets of scripts
#

target_dir="../pan-os_api.py-main"

for f in *.py; do
	echo $f
	diff $f $target_dir/$f
	read -t 10 -n 1 -p "Press any key to continue or wait for 10s or use ^C to stop now.."
done

exit