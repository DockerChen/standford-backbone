#!/bin/bash

# Read hosts
hosts=$(python ./pcap_interfaces.py)

# Prepare directory
pcaps="./pcaps"
rm -rf $pcaps
mkdir $pcaps

# Dump packets
for host in $hosts
do
	echo "Dump packets at: "$host
	sudo taskset -c 3 tcpdump icmp -i $host -nS -Uw $pcaps/$host.pcap &
done