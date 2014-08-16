#! /bin/sh

while true
do
	date
	count=$(sudo ovs-ofctl dump-flows s1008 | wc -l)
	if [ $count -eq 4 ]; then
		echo "Normal"
	else
		echo "Reinstall start"
		for line in $(cat rule_all.txt)
		do
			echo -n "."
			$line
		done
		sleep 10
		echo "Reinstall done"
	fi
	sleep 2
done