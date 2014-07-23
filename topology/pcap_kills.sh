#!/bin/bash

echo "Kill tcpdump sessions: "$(pidof tcpdump)
sudo kill -9 $(pidof tcpdump)