#! /bin/sh

while true
do
	date
	count=$(sudo ovs-ofctl dump-flows s1008 | wc -l)
	if [ $count -eq 4 ]; then
		echo "Normal"
	else
		echo "Reinstall start"
		./rule_installs.sh
		sleep 10
		echo "Reinstall done"
	fi
	sleep 2
done