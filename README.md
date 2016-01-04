## Getting Started
* The idea is to route ICMP traffic in the emulated Stanford-backbone network.
* Follow the [configuration instructions](https://github.com/wuyangjack/standford-backbone/blob/master/configuration/Notes.md) to generated the necessary OpenFlow rules (translated from the Stanford-backbone network). 
* Follow the [controller instructions](https://github.com/wuyangjack/standford-backbone/blob/master/controller/Notes.md) to setup the controller which would install the previously-generated OpenFlow rules into Mininet. 
* Follow the [topology instructions](https://github.com/wuyangjack/standford-backbone/blob/master/topology/Notes.md) to setup the Stanford-backbone topology in Mininet. Start controller before Mininet. Otherwise exisiting dummy flow entries might be cleared.
* From [mininet net output](https://github.com/wuyangjack/standford-backbone/blob/master/topology/net.txt)(`mininet> net`) we noticed the connection: `h197(h197-eth0) --- (s13-eth9)s13(s13-eth8) --- (h196-eth0)h196`. So h197 is where we want to initiate the ICMP traffic.
* Check what routes are available at s13 by `sudo ovs-ofctl dump-flows s13`. Observe this: `cookie=0x0, duration=3189.633s, table=0, n_packets=0, n_bytes=0, priority=59929,ip,nw_dst=128.12.1.248/29 actions=output:5,output:8,output:2`. So we can try to ping `128.12.1.249`. And if things work, the ICMP traffic should be forwarded to both `s13-eth2` and `s13-eth8` but not to any other ports.
* Prepare h197 to initiate ICMP traffic. 
  * View the route table by `h197 route -n`. Make sure the default route is present.
  * Setup static ARP by `h197 arp -s 128.12.1.249 01:00:00:00:00:23`. Without this, the PING client could not figure out what MAC address to use, i.e. some ARP protocol is required.
* Start ICMP traffic: `h197 ping 128.12.1.249`.
* Check if the ICMP traffic is forwarded properly.
  * Check if s13 receive the traffic: `sudo tcpdump icmp -i s13-eth9 -nS`. You should see ICMP traffic.
  * Check if s13 forward the traffic correctly: `sudo tcpdump icmp -i s13-eth2 -nS` & `sudo tcpdump icmp -i s13-eth8 -nS`. You should see ICMP traffic. `sudo tcpdump icmp -i s13-eth3 -nS`. You should not see ICMP traffic (and for all other ports except 2 & 8).
  * Ping should fail. Because we did not configure host IP.

## Ping Google
* Prepare h197 to initiate ICMP traffic to Google (74.125.226.78).
* Probe the path
  * Use the [topology information](https://github.com/wuyangjack/standford-backbone/blob/master/topology/net.txt) to figure out peering ports.
  * See what flow table entries are being matched by invert matching: `sudo ovs-ofctl dump-flows s13 | grep -v n_packets=0`
* The path of Google traffic: 
  ** `h197-eth0 > s13-eth9 > s13-eth1 > s1005-eth4 > s1005-eth1 > s2-eth13 > s2-eth4 > s1009-eth1 > s1009-eth2(s1009-eth3) > s3-eth1(s12-eth9) > s3-eth7(s12-eth1) > h67-eth0(s1007-eth3) > (s1007-eth1) > (s1-eth1) > (s1-eth4) > (h18-eth0)`
  8* It seems that the traffic is forwarded to two destinations. One is a border router (s1 is the bbra_rtr). Another is an operational zone router (s3 is boza_rtr).

## Ping Stanford
* Prepares h197 to initiate ICMP traffic to `stanford.cs.edu` (171.64.64.64).
* Probe the path: `h197-eth0 > s13-eth9 > s13-eth6 > s1006-eth3 > s1006-eth1 > s1-eth32 > s1-eth22 > h33-eth0`.
* Inject fault: 
  * Add a dropping rule by `sudo ovs-ofctl add-flow s1 dl_type=0x0800,nw_dst=171.64.64.64/32,priority=65535,actions=`
  * The previous traffic will be dropped. Run `sudo tcpdump -i s1-eth32 -nS` you should still see traffic. However, run `sudo tcpdump -i s1-eth22 -nS`, and you should not see traffic. Bascically, traffic is dropped at s1.
  * How to check if packets are received: If we dumped the traffic at at s1-eth22 ([pcap](https://github.com/wuyangjack/standford-backbone/blob/master/topology/data/s1-eth22.pcap)), we can see that traffic stops at the 58173th packet. We could filter the time interval by  `editcap -A "2014-8-11 13:51:28" -B "2014-8-11 13:52:00" s1-eth22.pcap time.pcap`. Then we can see if packets of interest did arrive: `time tshark -r time.pcap -R "(icmp and ip.src!=10.0.0.17)"`
  * If we dumped roughly 10 minutes of traffic (roughly 50 GB of headers):
    * The experiment happens on August 13, starts at 15:40, drops at 16:19, ends at 16:21.
    * No packet at s2017-eth1 (0.51 + 0.11 = 0.62 second).
    * No packet at s2017-eth2 (0.51 + 0.11 = 0.62 second).
    * No packet at s1-eth22 (0.49 + 0.11 = 0.60 second).
    * Packet at s1-eth32 (0.82 + 0.22 = 1.04 second).
    * Packet at other interfaces at s1 (estimated 6x more traffic, so 1.04 * 6 = 6.24 second).
    * Total pcap query latency is roughly 10 seconds. We touched roughly 15% of all the captured pcap traces.
