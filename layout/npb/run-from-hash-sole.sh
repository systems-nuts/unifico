#!/usr/bin/expect -f

set experiment [lindex $argv 0]
set class [lindex $argv 1]
set bin_type [lindex $argv 2]
set iterations [lindex $argv 3]

spawn sshpass -f "/home/nikos/docs/pass.txt" ssh nikos@sole
expect "$ "

send "cd ~/phd/unified_abi/layout/npb/ \r"
expect "$ "

send "./run.sh $experiment $class aarch64 $bin_type $iterations \r"
while {1} {
	expect {
		-re "Done." break
	}
}

send "exit \r"
expect "$ "
