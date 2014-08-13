#!/bin/bash

# Due to memory problems
# We sample data rates at ports instead of dumping them all at once

# Read hosts
hosts=$(python ./pcap_interfaces_all.py)

# Prepare directory
pcaps="./rates"
rm -rf $pcaps
mkdir $pcaps

# Dump packets
for host in $hosts
do
	echo "Sample rates at: "$host
	sudo tcpdump icmp -i $host -nS -Uw $pcaps/$host.pcap &
	sleep 2; kill $!
done