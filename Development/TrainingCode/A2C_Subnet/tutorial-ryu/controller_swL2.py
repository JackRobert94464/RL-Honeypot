# -*- coding: utf-8 -*-

"""
Ryu Layer 2 Learning Switch

Note: Requires Python3.8 or higher (uses the ':=' operator)
"""
from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet.ethernet import ethernet
from ryu.lib.packet.ipv6 import ipv6
from ryu.lib.packet.lldp import lldp
from ryu.lib.dpid import dpid_to_str


class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    ILLEGAL_PROTOCOLS = [ipv6, lldp]

    def __init__(self, *args, **kwargs):
        '''
        Init | Constructor
        '''
        super(Controller, self).__init__(*args, **kwargs)
        self.mac_port_map = {}


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        '''
        Handshake: Features Request Response Handler
        '''
        datapath = ev.msg.datapath
        match = datapath.ofproto_parser.OFPMatch()
        actions = [datapath.ofproto_parser.OFPActionOutput(datapath.ofproto.OFPP_CONTROLLER, datapath.ofproto.OFPCML_NO_BUFFER)]
        self.mac_port_map[dpid_to_str(datapath.id)] = {}
        self.__add_flow(datapath, 0, match, actions, idle=0)
        self.logger.info("🤝\thandshake taken place with datapath: {}".format(dpid_to_str(datapath.id)))

    @set_ev_cls(ofp_event.EventOFPErrorMsg, [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
        '''
        OpenFlow Error Handler
        '''
        error = ev.msg.datapath.ofproto.ofp_error_to_jsondict(ev.msg.type, ev.msg.code)
        self.logger.error("🆘\topenflow error received:\n\t\ttype={}\n\t\tcode={}".format(error.get("type"), error.get("code")))

    @ set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        '''
        Packet In Event Handler
        '''
        datapath = ev.msg.datapath
        self.logger.debug("❗️\tevent 'packet in' from datapath: {}".format(dpid_to_str(datapath.id)))
        pkt = packet.Packet(ev.msg.data)
        in_port = ev.msg.match['in_port']
        if self.__illegal_packet(pkt):
            return

        # Set defaults
        actions = [datapath.ofproto_parser.OFPActionOutput(datapath.ofproto.OFPP_FLOOD)]

        # Only perform layer 2 learning if packet has an ethernet header
        if eth_header := pkt.get_protocol(ethernet):

            # add/update the layer 2 information to the controller's global map
            self.mac_port_map[dpid_to_str(datapath.id)][eth_header.src] = in_port
            # (here it could be also added to the flow table...)
            
            # check if current packet has known egress port
            if port := self.mac_port_map.get(dpid_to_str(datapath.id), {}).get(eth_header.dst, None):
                # set output port to be known port, overwriting the FLOOD directive
                actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                # install this logic to the datapath's flow table
                match = datapath.ofproto_parser.OFPMatch(eth_dst=eth_header.dst)
                self.__add_flow(datapath, 1, match, actions)
                
        # Send the packet out
        pkt_out_msg = datapath.ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=ev.msg.buffer_id, in_port=in_port, actions=actions, data=ev.msg.data)
        datapath.send_msg(pkt_out_msg)
        return

    def __illegal_packet(self, pkt, log=True):
        '''
        Illegal Packet Check
        '''
        for proto in self.ILLEGAL_PROTOCOLS:
            if pkt.get_protocol(proto) and log:
                if log:
                    self.logger.debug("🚨\tpacket with illegal protocol seen: {}".format(proto.__name__))
                return True
        return False

    def __add_flow(self, datapath, priority, match, actions, idle=60, hard=0):
        '''
        Install Flow Table Modification
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst, idle_timeout=idle, hard_timeout=hard)
        self.logger.info("✍️\tflow-Mod written to datapath: {}".format(dpid_to_str(datapath.id)))
        datapath.send_msg(mod)
