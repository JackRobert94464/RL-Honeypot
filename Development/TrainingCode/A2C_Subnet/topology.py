from mininet.topo import Topo
from mininet.link import TCLink

class TutorialTopology( Topo ):

  def build( self ):
    # add a host to the network
    h1 = self.addHost( 'h1' )
    h2 = self.addHost( 'h2' )
    h3 = self.addHost( 'h3' )
    h4 = self.addHost( 'h4' )
    h5 = self.addHost( 'h5' )

    h6 = self.addHost( 'h6' )
    h7 = self.addHost( 'h7' )
    h8 = self.addHost( 'h8' )
    h9 = self.addHost( 'h9' )
    h10 = self.addHost( 'h10' )
    
    # add a switch to the network
    s1 = self.addSwitch( 's1' )
    s2 = self.addSwitch( 's2' )

    # add a link between the host `h1-h5` and the `s1` switch
    # self.addLink( h1, s1 )
    # self.addLink( h2, s1 )
    # self.addLink( h3, s1 )
    self.addLink( h4, s1 )
    self.addLink( h5, s1 )
    
    # add a link between the host `h6-h10` switch and the `s2` switch
    
    self.addLink( h6, s2 )
    self.addLink( h7, s2 )
    self.addLink( h8, s2 )
    self.addLink( h9, s2 )
    self.addLink( h10, s2 )
    
    # add a link between the `s1` switch and the `s2` switch
    # self.addLink( s1, s2 )
    self.addLink( s1, s2, cls=TCLink, bw=50, delay='30ms', loss=10)
    
    # add bandwidth to the links
    # add a link between s1 and h1 with a max bandwidth of 100Mbps
    self.addLink(h1, s1, cls=TCLink, bw=100)
    
    # add a link between s1 and h2 with a minimum delay of 75ms
    self.addLink(h2, s1, cls=TCLink, delay='75ms')
    
    # add a link between s1 and h3 with 5% packet loss
    self.addLink(h3, s1, cls=TCLink, loss=5)



# the topologies accessible to the mn tool's `--topo` flag
# note: if using the Dockerfile, this must be the same as in the Dockerfile
topos = { 'tutorialTopology': ( lambda: TutorialTopology() ) }
