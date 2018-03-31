#!/usr/bin/env python

from math import pow
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class Tree(Topo):
    "Simple Data Center Topology"
    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"

    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        # Adds core switches
        self.createSwitches('cs', fanout, 0)
        # Adds aggregation switches
        self.createSwitches('as', fanout, 1)
        # Adds edge switches
        self.createSwitches('es', fanout, 2)
        # Adds hosts
        self.createHosts('h', fanout, 3)
        # Adds links
        self.createLinks('cs', 'as', fanout, 1)
        self.createLinks('as', 'es', fanout, 2)
        self.createLinks('es', 'h', fanout, 3)

    # Create switches
    def createSwitches(self, label, fanout, level):
        for x in range(int(pow(fanout, level))):
            self.addSwitch(label + str(x))

    # Create hosts
    def createHosts(self, label, fanout, levels):
        for x in range(int(pow(fanout, levels))):
            self.addHost(label + str(x))

    # Create links
    def createLinks(self, abovelabel, thislabel, fanout, level):
        for x in range(int(pow(fanout, level - 1))):
            for y in range(fanout * x ,fanout * (x + 1)):
                aboveSwich = abovelabel + str(x)
                thisSwitch = thislabel + str(y)
                self.addLink(aboveSwich, thisSwitch)



def perfTest():
    "Create network and run simple performance test"
    topo = Tree(1, 2, 3)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, cleanup=True)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections( net.hosts )
    print "Testing network connectivity"
    net.pingAll()
    print "Testing bandwidth between h1 and h4"
    h1, h2 = net.get( 'h1', 'h2' )
    net.iperf( (h1, h2) )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()
