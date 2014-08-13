#!/usr/bin/env python

"Get all interfaces that needs to be tcpdumped"

inputFile = "./net_samples.txt"

# Scan for nodes and edges
with open(inputFile) as f:
    for line in f:
        if line[0:1] == "s" and line[0:4] != "s100":
            tokens = line.strip().split()
            for token in tokens:
                if token.find(":") != -1 and token != "lo:":
                    ports = token.strip().split(":")
                    # Tweak to avoid memory crash
                    # Only print relevant ports (s1,s2017)
                    if ports[0].startswith("s1-") or ports[0].startswith("s2017-"):
                        print ports[0]
