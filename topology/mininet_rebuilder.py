#!/usr/bin/env python

'''
    Copyright (C) 2012  Stanford University

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    Description: Load topology in Mininet 2.0
    Author: James Hongyi Zeng (hyzeng_at_stanford.edu)
            Yang (Jack) Wu (yangwu6@cis.upenn.edu)
'''

from argparse import ArgumentParser
from socket import gethostbyname
from os import getuid

from mininet.log import lg, info
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import Link, Intf
from mininet.node import Host, OVSKernelSwitch, Controller, RemoteController
from mininet.node import OVSController

class StanfordTopo( Topo ):
    "Topology for Stanford backbone"

    PORT_ID_MULTIPLIER = 1
    INTERMEDIATE_PORT_TYPE_CONST = 1
    OUTPUT_PORT_TYPE_CONST = 2
    PORT_TYPE_MULTIPLIER = 10000
    SWITCH_ID_MULTIPLIER = 100000
    
    DUMMY_SWITCH_BASE = 1000
    
    PORT_MAP_FILENAME = "data/port_map.txt"
    TOPO_FILENAME = "data/backbone_topology.tf"
    
    dummy_switches = set()
    # Jack
    dummy_rules = list()

    def __init__( self ):
        # Read topology info
        ports = self.load_ports(self.PORT_MAP_FILENAME)
        links = self.load_topology(self.TOPO_FILENAME)
        switches = ports.keys()

        # Add default members to class.
        super( StanfordTopo, self ).__init__()

        # Create switch nodes
        for s in switches:
            # Jack
            print "add_switch(): s%s" % s
            self.addSwitch( "s%s" % s )

        # Wire up switches       
        self.create_links(links, ports)
        
        # Wire up hosts
        host_id = len(switches) + 1
        for s in switches:
            # Edge ports
            for port in ports[s]:
                # Jack
                print "add_host(): h%s" % host_id
                self.addHost( "h%s" % host_id )
                print "add_link(): nodes h%s to s%s, ports %d to %d (host)" % (host_id, s, 0, port)
                self.addLink( "h%s" % host_id, "s%s" % s, 0, port )
                host_id += 1

        # Consider all switches and hosts 'on'
        # self.enable_all()
            
    def load_ports(self, filename):
        ports = {}
        f = open(filename, 'r')
        for line in f:
            if not line.startswith("$") and line != "":
                tokens = line.strip().split(":")
                port_flat = int(tokens[1])
                
                dpid = port_flat / self.SWITCH_ID_MULTIPLIER
                port = port_flat % self.PORT_TYPE_MULTIPLIER
                
                if dpid not in ports.keys():
                    ports[dpid] = set()
                if port not in ports[dpid]:
                    ports[dpid].add(port)             
        f.close()
        return ports
        
    def load_topology(self, filename):
        links = set()
        f = open(filename, 'r')
        for line in f:
            if line.startswith("link"):
                tokens = line.split('$')
                src_port_flat = int(tokens[1].strip('[]').split(', ')[0])
                dst_port_flat = int(tokens[7].strip('[]').split(', ')[0])
                links.add((src_port_flat, dst_port_flat))
        f.close()
        return links
        
    def create_links(self, links, ports):  
        '''Generate dummy switches
           For example, interface A1 connects to B1 and C1 at the same time. Since
           Mininet uses veth, which supports point to point communication only,
           we need to manually create dummy switches

        @param links link info from the file
        @param ports port info from the file
        ''' 
        # First pass, find special ports with more than 1 peer port
        first_pass = {}
        for (src_port_flat, dst_port_flat) in links:
            src_dpid = src_port_flat / self.SWITCH_ID_MULTIPLIER
            dst_dpid = dst_port_flat / self.SWITCH_ID_MULTIPLIER
            src_port = src_port_flat % self.PORT_TYPE_MULTIPLIER
            dst_port = dst_port_flat % self.PORT_TYPE_MULTIPLIER
            
            if (src_dpid, src_port) not in first_pass.keys():
                first_pass[(src_dpid, src_port)] = set()
            first_pass[(src_dpid, src_port)].add((dst_dpid, dst_port))
            if (dst_dpid, dst_port) not in first_pass.keys():
                first_pass[(dst_dpid, dst_port)] = set()
            first_pass[(dst_dpid, dst_port)].add((src_dpid, src_port))
            
        # Second pass, create new links for those special ports
        dummy_switch_id = self.DUMMY_SWITCH_BASE
        for (dpid, port) in first_pass.keys():
            # Special ports!
            if(len(first_pass[(dpid,port)])>1):
                # Jack
                # Generate dummy rules
                self.generate_dummy_rules(dummy_switch_id, len(first_pass[(dpid,port)]))

                # Jack
                print "add_switch(): s%s (dummy)" % dummy_switch_id
                self.addSwitch( "s%s" % dummy_switch_id )
                self.dummy_switches.add(dummy_switch_id)
                
                # Jack
                print "add_link(): nodes s%s to s%s, ports %d to %d (to dummy)" % (dpid, dummy_switch_id, port, 1)
                self.addLink( node1="s%s" % dpid, node2="s%s" % dummy_switch_id, port1=port, port2=1 )
                dummy_switch_port = 2
                for (dst_dpid, dst_port) in first_pass[(dpid,port)]:
                    first_pass[(dst_dpid, dst_port)].discard((dpid,port))
                    # Jack
                    print "add_link(): nodes s%s to s%s, ports %d to %d (from dummy)" % (dummy_switch_id, dst_dpid, dummy_switch_port, dst_port)
                    self.addLink( node1="s%s" % dummy_switch_id, node2="s%s" % dst_dpid, port1=dummy_switch_port, port2=dst_port)
                    ports[dst_dpid].discard(dst_port)
                    dummy_switch_port += 1
                dummy_switch_id += 1  
                first_pass[(dpid,port)] = set()    
            ports[dpid].discard(port)
        
        # Third pass, create the remaining links
        for (dpid, port) in first_pass.keys():
            for (dst_dpid, dst_port) in first_pass[(dpid,port)]:
                # Jack
                print "add_link(): nodes s%s to s%s, ports %d to %d (normal)" % (dpid, dst_dpid, port, dst_port)
                self.addLink( node1="s%s" % dpid, node2="s%s" % dst_dpid, port1=port, port2=dst_port )
                ports[dst_dpid].discard(dst_port)     
            ports[dpid].discard(port)          
        
     # Jack
    def generate_dummy_rules(self, dummy_switch_id, port_count):
        ingress = "sudo ovs-ofctl add-flow s%s dl_type=0x0800,in_port=1,actions=" % (dummy_switch_id)
        for dst_port in range(2, port_count + 2):
            ingress += "output:%d," % dst_port
            self.dummy_rules.append("sudo ovs-ofctl add-flow s%s dl_type=0x0800,in_port=%d,actions=output:1" % (dummy_switch_id, dst_port))
        ingress = ingress[:-1]
        self.dummy_rules.append(ingress)

class StanfordMininet ( Mininet ):

    def build( self ):
        super( StanfordMininet, self ).build()
        
        # FIXME: One exception... Dual links between yoza and yozb
        # Need _manual_ modification for different topology files!!!
        self.topo.addLink( node1="s%s" % 15, node2="s%s" % 16, port1=7, port2=4 )

# Jack
# Discard dummy controller parameters
# def StanfordTopoTest( controller_ip, controller_port, dummy_controller_ip, dummy_controller_port ):
def StanfordTopoTest( controller_ip, controller_port ):
    topo = StanfordTopo()

    main_controller = lambda a: RemoteController( a, ip=controller_ip, port=controller_port)
    net = StanfordMininet( topo=topo, switch=OVSKernelSwitch, controller=main_controller)
    
    net.start()

    # Jack
    # Dummy controller not used
    # Instead use ovs-ofctl to install pre-computed dummy rules
    '''
    # These switches should be set to a local controller..
    dummy_switches = topo.dummy_switches
    dummyClass = lambda a: RemoteController( a, ip=dummy_controller_ip, port=dummy_controller_port)
    dummy_controller = net.addController( name='dummy_controller', controller=dummyClass)
    dummy_controller.start()
    
    for dpid in dummy_switches:
        switch = net.nameToNode["s%s" % dpid]
        # Jack
        # switch.pause()
        switch.start( [dummy_controller] )
    '''

    # Jack
    # STP truned off
    # Otherwise, dummy ports might be down, causing connectivity problem
    '''    
    # Turn on STP  
    for switchName in topo.switches():
        switch = net.nameToNode[switchName]
        cmd = "ovs-vsctl set Bridge %s stp_enable=true" % switch.name
        switch.cmd(cmd)
        
    switch.cmd('ovs-vsctl set Bridge s1 other_config:stp-priority=0x10')
    '''

    # Jack
    # Install dummy rules
    switch = net.nameToNode["s1001"]
    for rule in topo.dummy_rules:
        result = switch.cmd(rule)
        print "Installing dummy rule: %s, returns: " % rule, result
    
    # Jack
    # Prepare hosts
    for hostName in topo.hosts():
        host = net.nameToNode[hostName]
        # Set default route at hosts, forwarding all traffic to access switch
        # Otherwise PING complains no route
        cmd = "route add default dev %s-eth0" % host.name
        result = host.cmd(cmd)
        if len(result) != 0:
            raise Exception("error")
        print "Setting up default route: %s, returns: #%s#" % (cmd, result)
        # Set static ARP protocol
        # Otherwise needs to setup ARP
        cmd = "arp -s 171.64.64.64 01:00:00:00:00:23"
        result = host.cmd(cmd)
        if len(result) != 0:
            raise Exception("error")
        print "Setting up static ARP: %s, returns: %s" % (cmd, result)
        # Initiate ping traffic
        cmd = "ping 171.64.64.64 &"
        result = host.cmd(cmd)
        print "Traffic: %s, returns: %s" % (cmd, result)

    CLI( net )
    net.stop()

if __name__ == '__main__':
    if getuid()!=0:
        print "Please run this script as root / use sudo."
        exit(-1)

    lg.setLogLevel( 'info')
    description = "Put Stanford backbone in Mininet"
    parser = ArgumentParser(description=description)
    parser.add_argument("-c", dest="controller_name",
                      default="localhost",
                      help="Controller's hostname or IP")
    parser.add_argument("-p", dest="controller_port",type=int,
                      default=7733,
                      help="Controller's port")

    # Jack: discard dummy controller parameters
    '''
    parser.add_argument("-c2", dest="dummy_controller_name",
                      default="localhost",
                      help="Dummy controller's hostname or IP")
    parser.add_argument("-p2", dest="dummy_controller_port",type=int,
                      default=6633,
                      help="Dummy ontroller's port")
    '''

    args = parser.parse_args()
    print description
    print "Starting with primary controller %s:%d" % (args.controller_name, args.controller_port)
    # Jack
    #print "Starting with dummy controller %s:%d" % (args.dummy_controller_name, args.dummy_controller_port)
    topo = StanfordTopo()
    Mininet.init()
    StanfordTopoTest(gethostbyname(args.controller_name), args.controller_port)
    # Jack
    # StanfordTopoTest(gethostbyname(args.controller_name), args.controller_port, gethostbyname(args.dummy_controller_name), args.dummy_controller_port)

