## Authors
* Yang (Jack) Wu (yangwu6@cis.upenn.edu)
* James Hongyi Zeng (hyzeng_at_stanford.edu)
* Peyman Kazemian (kazemian_at_stanford.edu)

## Getting Started
* The idea is to route ICMP traffic in the emulated Stanford-backbone network.
* Follow the [configuration instructions](https://github.com/wuyangjack/standford-backbone/blob/master/configuration/Notes.md) to generated the necessary OpenFlow rules (translated from the Stanford-backbone network). 
* Follow the [controller instructions](https://github.com/wuyangjack/standford-backbone/blob/master/controller/Notes.md) to setup the controller which would install the previously-generated OpenFlow rules into Mininet.
* Follow the [topology instructions](https://github.com/wuyangjack/standford-backbone/blob/master/topology/Notes.md) to setup the Stanford-backbone topology in Mininet.
* From [mininet net output](https://github.com/wuyangjack/standford-backbone/blob/master/topology/net.txt)(`mininet> net`) we noticed the connection: `h197(h197-eth0) --- (s13-eth9)s13(s13-eth8) --- (h196-eth0)h196`. So h197 is where we want to initiate the ICMP traffic.
* Check what routes are available at s13 by `sudo ovs-ofctl dump-flows s13`. Observe this: `cookie=0x0, duration=3189.633s, table=0, n_packets=0, n_bytes=0, priority=59929,ip,nw_dst=128.12.1.248/29 actions=output:5,output:8,output:2`. So we can try to ping `128.12.1.249`. And if things work, the ICMP traffic should be forwarded to both `s13-eth2` and `s13-eth8` but not to any other ports.
* Prepare h197 to initiate ICMP traffic. 
  * Add an default route by `h197 route add default dev h197-eth0`. Without this, h197 does not know how to route traffic other than 10.0.0.1/24 destinations. View the route table by `h197 router -n`.
  * Setup static ARP by `h197 arp -s 128.12.196.123 01:00:00:00:00:23`. Without this, the PING client could not figure out what MAC address to use, i.e. some ARP protocol is required.
* Start ICMP traffic: `h197 ping 128.12.1.249`.
* Check if the ICMP traffic is forwarded properly.
  * Check if s13 receive the traffic: `sudo tcpdump icmp -i s13-eth9 -nS`. You should see ICMP traffic.
  * Check if s13 forward the traffic correctly: `sudo tcpdump icmp -i s13-eth2 -nS` & `sudo tcpdump icmp -i s13-eth8 -nS`. You should see ICMP traffic. `sudo tcpdump icmp -i s13-eth3 -nS`. You should see ICMP traffic (and for all other ports except 2 & 8).
  * Ping should fail. Because we did not configure host IP.

