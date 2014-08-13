#!/usr/bin/env python

"Get all interfaces that needs to be tcpdumped"

inputFile = "./net.txt"

# Scan for nodes and edges
with open(inputFile) as f:
    for line in f:
        if line[0:1] == "s" and line[0:4] != "s100":
            tokens = line.strip().split()
            for token in tokens:
                if token.find(":") != -1 and token != "lo:":
                    ports = token.strip().split(":")
                    # Tweak to avoid memory crash
                    # Should end up with 48 switches
                    # if ports[0].endswith("eth1") or ports[0].endswith("eth2") or ports[0].endswith("eth3"):
                    # 	print ports[0]
                    print ports[0]
