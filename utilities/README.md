### Turn on all cpus 
```
for((i=1;i<=15;i++)); do sudo bash -c "echo 1 >/sys/devices/system/cpu/cpu${i}/online";done
```
