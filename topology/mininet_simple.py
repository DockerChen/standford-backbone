#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController
from mininet.node import Host
from mininet.node import OVSSwitch
from mininet.node import Controller
from mininet.link import Link
from mininet.cli import CLI

class SimpleTopo(Topo):
    "Single switch connected to n hosts."
    def __init__(self, n=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        host = self.addHost('h1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)
        # Change ip

topos = { 'simpletopo': ( lambda: SimpleTopo() ) }

def simpleTest():
    "Create and test a simple network"
    topo = SimpleTopo(n=2)
    net = Mininet(topo, controller = OVSController)
    h1 = net.get('h1')
    h2 = net.get('h2')
    h1.setIP( '192.168.1.1/24' )
    print h1.IP()                                                                                         
    h2.setIP( '192.168.1.2/24' )
    print h2.IP()                                                                                 
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
    '''
    h1 = Host( 'h1' )                                                                                                     
    h2 = Host( 'h2' )                                                                                                     
    s1 = OVSSwitch( 's1', inNamespace=False )                                                                             
    c0 = OVSController( 'c0', inNamespace=False )                                                                            
    Link( h1, s1 )                                                                                                        
    Link( h2, s1 )                                                                                                        
    h1.setIP( '192.168.1.1/24' )
    print h1.IP()                                                                                         
    h2.setIP( '192.168.1.2/24' )                                                                                                  
    c0.start()                                                                                                            
    s1.start( [ c0 ] )
    print h1.cmd( 'ping -c1', h2.IP() )                                                                                   
    s1.stop()                                                                                                             
    c0.stop() 
    '''