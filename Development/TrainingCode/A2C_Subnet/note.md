general consensus: if nodes is conencted to same switch with no forbidden rule, then all nodes in same swtich is connected together and have EPSS between connections.

So as part of our mininet simulation, i'm setting up a code that will automatically update a mongoDB data on the topology so that our RL-agent can have a NTPG to use for prediction. I first run the topologyHoneypotSDN code, which will output the information you will see below. Can you help me write a code to import the data dumped from mininet into the correct format and save it to the mongoDB that i will attach a sample below? If possible, can you help me build a CVE check code that use something like opensource tool to retrieve the CVE for each host, then just print the CVE name out to screen as it dumping the mininet topology (this is future plan so dont worry if u make mistake). The important part is the mininet to mongoDB. note that subnet is related to the switch that the hosts are connecting too (that's their subnet) and EPSS is the afterwork i mention earlier of which after i got a bunch of names for what hosts with what CVEs i can use EPSS to give me API on the score then average it to turn it into the EPSS point.

This is the sample output after a mininet network is created in our simulation:

ubuntu@ubuntu-virtual-machine:~/RL-Honeypot-linux/Development/TrainingCode/A2C_Subnet/tutorial-ryu$ sudo python topologyHoneypotSDN.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h32 h1337 
*** Adding switches:
s1 s2 s3 s4 s111 
*** Adding links:
(h1, s1) (h2, s1) (h3, s2) (h4, s2) (h5, s2) (h6, s3) (h7, s3) (h8, s3) (h9, s4) (h10, s4) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (s1, s111) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (s2, s111) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (s3, s111) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (s4, s111) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (s111, h32) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (s111, h1337) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h32 h1337 
*** Starting controller
c2 
*** Starting 5 switches
s1 s2 s3 s4 s111 ...(50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) (50.00Mbit 30ms delay 10.00000% loss) 
('h1', 874974)
('h2', 874976)
('h3', 874978)
('h4', 874980)
('h5', 874982)
('h6', 874984)
('h7', 874986)
('h8', 874988)
('h9', 874990)
('h10', 874992)
('h32', 874994)
('h1337', 874996)
('c2', 874967)
Dumping networks connections
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s2-eth1
h4 h4-eth0:s2-eth2
h5 h5-eth0:s2-eth3
h6 h6-eth0:s3-eth1
h7 h7-eth0:s3-eth2
h8 h8-eth0:s3-eth3
h9 h9-eth0:s4-eth1
h10 h10-eth0:s4-eth2
h32 h32-eth0:s111-eth6
h1337 h1337-eth0:s111-eth5
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:s111-eth1
s2 lo:  s2-eth1:h3-eth0 s2-eth2:h4-eth0 s2-eth3:h5-eth0 s2-eth4:s111-eth2
s3 lo:  s3-eth1:h6-eth0 s3-eth2:h7-eth0 s3-eth3:h8-eth0 s3-eth4:s111-eth3
s4 lo:  s4-eth1:h9-eth0 s4-eth2:h10-eth0 s4-eth3:s111-eth4
s111 lo:  s111-eth1:s1-eth3 s111-eth2:s2-eth4 s111-eth3:s3-eth4 s111-eth4:s4-eth3 s111-eth5:h1337-eth0 s111-eth6:h32-eth0
c2
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:s111-eth1
s2 lo:  s2-eth1:h3-eth0 s2-eth2:h4-eth0 s2-eth3:h5-eth0 s2-eth4:s111-eth2
s3 lo:  s3-eth1:h6-eth0 s3-eth2:h7-eth0 s3-eth3:h8-eth0 s3-eth4:s111-eth3
s4 lo:  s4-eth1:h9-eth0 s4-eth2:h10-eth0 s4-eth3:s111-eth4
s111 lo:  s111-eth1:s1-eth3 s111-eth2:s2-eth4 s111-eth3:s3-eth4 s111-eth4:s4-eth3 s111-eth5:h1337-eth0 s111-eth6:h32-eth0
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s2-eth1
h4 h4-eth0:s2-eth2
h5 h5-eth0:s2-eth3
h6 h6-eth0:s3-eth1
h7 h7-eth0:s3-eth2
h8 h8-eth0:s3-eth3
h9 h9-eth0:s4-eth1
h10 h10-eth0:s4-eth2
h32 h32-eth0:s111-eth6
h1337 h1337-eth0:s111-eth5
s1 lo:0 s1-eth1:1 s1-eth2:2 s1-eth3:3 
s2 lo:0 s2-eth1:1 s2-eth2:2 s2-eth3:3 s2-eth4:4 
s3 lo:0 s3-eth1:1 s3-eth2:2 s3-eth3:3 s3-eth4:4 
s4 lo:0 s4-eth1:1 s4-eth2:2 s4-eth3:3 
s111 lo:0 s111-eth1:1 s111-eth2:2 s111-eth3:3 s111-eth4:4 s111-eth5:5 s111-eth6:6 
Testing network connectivity
Finished initializing important healthcheck service. Hit port 15000 to imitate compromise.


This is the mongoDB data that i want to achieve.


# Sample static topo dict
topo_dict = {
    "nodes": [
        {
            "node_name": "h1",
            "node_EPSS": 0.7,
            "node_ipv4": '10.0.0.1',
            "node_subnet": "s1"
        },
        {
            "node_name": "h2",
            "node_EPSS": 0.5,
            "node_ipv4": '10.0.0.2',
            "node_subnet": "s1"
        },
        {
            "node_name": "h3",
            "node_EPSS": 0.3,
            "node_ipv4": '10.0.0.3',
            "node_subnet": "s2"
        },
        {
            "node_name": "h4",
            "node_EPSS": 0.65,
            "node_ipv4": '10.0.0.4',
            "node_subnet": "s2"
        },
        {
            "node_name": "h5",
            "node_EPSS": 0.4,
            "node_ipv4": '10.0.0.5',
            "node_subnet": "s2"
        },
        {
            "node_name": "h6",
            "node_EPSS": 0.55,
            "node_ipv4": '10.0.0.6',
            "node_subnet": "s3"
        },
        {
            "node_name": "h7",
            "node_EPSS": 0.45,
            "node_ipv4": '10.0.0.7',
            "node_subnet": "s3"
        },
        {
            "node_name": "h8",
            "node_EPSS": 0.35,
            "node_ipv4": '10.0.0.8',
            "node_subnet": "s3"
        },
        {
            "node_name": "h9",
            "node_EPSS": 0.5,
            "node_ipv4": '10.0.0.9',
            "node_subnet": "s4"
        },
        {
            "node_name": "h10",
            "node_EPSS": 0.6,
            "node_ipv4": '10.0.0.10',
            "node_subnet": "s4"
        }
    ]
}