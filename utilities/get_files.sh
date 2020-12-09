#!/usr/bin/expect -f

set timeout 60

set folder_name bla

set folder_name [lindex $argv 0]

spawn ssh nikos@129.215.165.71
expect "$ "
send "scp nikos@sole:temp.txt .\r"
expect "$ "
send "exit\r"
expect "$ "
spawn scp nikos@129.215.165.71:temp.txt .
expect "$ "
