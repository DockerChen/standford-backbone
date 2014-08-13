#!/bin/bash

# Due to memory problems
# We only select only relevant interfaces

# Read hosts
hosts=$(python ./pcap_interfaces_samples.py)

# Prepare directory
pcaps="./samples"
rm -rf $pcaps
mkdir $pcaps

# Dump packets
for host in $hosts
do
	echo "Dump packets at: "$host
	sudo tcpdump icmp -i $host -nS -Uw $pcaps/$host.pcap &
done