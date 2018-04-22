#!/usr/bin/env python

import argparse
from math import pow
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

# Core switch is the first level of our tree architecture
CORE_LEVEL = 0
# Access switches are the second level of our tree architecture
ACCESS_LEVEL = 1
# Edge switches are the third level of our tree architecture
EDGE_LEVEL = 2
# Hosts are the fourth level of our tree architecture
HOST_LEVEL = 3


class FatTree(Topo):

    def __init__(self, alopts, elopts, hlopts, fanout, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        # Adds core switches
        self.createSwitches('cs', fanout, CORE_LEVEL)
        # Adds aggregation switches
        self.createSwitches('as', fanout, ACCESS_LEVEL)
        # Adds edge switches
        self.createSwitches('es', fanout, EDGE_LEVEL)
        # Adds hosts
        self.createHosts('h', fanout, HOST_LEVEL)
        # Adds links
        self.createLinks('cs', 'as', alopts, fanout, ACCESS_LEVEL)
        self.createLinks('as', 'es', elopts, fanout, EDGE_LEVEL)
        self.createLinks('h', 'es', hlopts, fanout, HOST_LEVEL)

    # Create switches
    def createSwitches(self, label, fanout, level):
        if level == CORE_LEVEL:
            n = int(pow(fanout/2, 2))
        else:
            n = int((fanout/2)*fanout)

        for x in range(n):
            self.addSwitch(label + str(x))

    # Create hosts
    def createHosts(self, label, fanout, levels):
        for x in range(int(pow(fanout/2, 2) * fanout)):
            self.addHost(label + str(x))

    # Create links
    def createLinks(self, abovelabel, thislabel, linkopts, fanout, level):
        if level == ACCESS_LEVEL:
            rangeAbove = int(pow(fanout/2, 2))
        elif level == HOST_LEVEL:
            rangeAbove = int(pow(fanout/2, 2) * fanout)
        else:
            rangeAbove = int((fanout/2)*fanout)

        for x in range(int((fanout/2)*fanout)):
            for y in range(int(fanout/2)):
                posAbove = int((fanout/2 * x  + y) % rangeAbove)
                aboveSwich = abovelabel + str(posAbove)
                thisSwitch = thislabel + str(x)
                self.addLink(aboveSwich, thisSwitch, **linkopts)


def perfTest(alopts, elopts, hlopts, fanout):
    "Create network and run simple performance test"
    topo = FatTree(alopts, elopts, hlopts, fanout)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, cleanup=True)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    last_host_id = pow(fanout, HOST_LEVEL) - 1
    print "Testing bandwidth between h0 and h%d" % last_host_id
    hs, hc = net.get('h0', 'h%d' % last_host_id)
    net.iperf((hs, hc))
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    # fanout argument
    ap.add_argument("-f", "--fanout", default=2, required=False, help="fanout number")
    # access link throughput argument
    ap.add_argument("-al", "--accessLink", default=20, required=False, help="access link throughput")
    # edge link throughput argument
    ap.add_argument("-el", "--edgeLink", default=10, required=False, help="edge link throughput")
    # host link throughput argument
    ap.add_argument("-hl", "--hostLink", default=1, required=False, help="host link throughput")
    args = vars(ap.parse_args())
    alopts = dict(bw=int(args["accessLink"]))
    elopts = dict(bw=int(args["edgeLink"]))
    hlopts = dict(bw=int(args["hostLink"]))
    fanout = int(args["fanout"])
    perfTest(alopts, elopts, hlopts, fanout)