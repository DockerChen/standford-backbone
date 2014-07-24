#!/bin/bash

gnome-terminal --working-directory /home/jackwu/Projects/standford-backbone/ \
	--tab -t "Git" -e "bash" \
	--tab -t "Htop" -e "htop" \
	--tab -t "Eclipse" -e "/home/jackwu/eclipse/eclipse" \
	--tab -t "Mininet" -e "bash" \
	--tab -t "Sublime" -e "sublime-text" \
	--tab -t "Pcap" -e "bash" \
	--tab -t "Other" -e "bash"