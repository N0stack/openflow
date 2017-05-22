from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from L2Static import L2StaticEntry
from L2Dynamic import L2DynamicEntry


class L2Operation(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2Operation, self).__init__(*args, **kwargs)
        self.SwichOperation = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        did = ev.msg.datapath.id
        print(did)
        if(did == 4097):
            self.register_switch(did, "172.16.1.1", "11:11:11:11:11:11", "172.16.1.1", "255.255.255.0", 1, True, True, ev)
            self.SwichOperation[did]["static"].register_vm("1a:d0:63:c3:9e:2d", 3, ev)
        if(did == 4098):
            self.register_switch(did, "172.16.2.1", "11:11:11:11:11:11", "172.16.2.1", "255.255.255.0", 1, True, True, ev)
            self.SwichOperation[did]["static"].register_vm("56:0a:9c:e6:86:3e", 4, ev)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        cookie = msg.cookie
        port = msg.match['in_port']
        data = msg.data
        self.SwichOperation[datapath.id]["dynamic"].method[cookie](msg, datapath, port, data)

    def register_switch(self, did, ip, mac, subnet_ip, subnet_mask, port, L2out, L3, ev):
        self.SwichOperation[did] = {
            "static": L2StaticEntry(mac=mac, port=port, subnet_ip=subnet_ip, subnet_mask=subnet_mask, L2out=L2out, L3=L3, ev=ev),
            "dynamic": L2DynamicEntry(ip=ip, mac=mac, port=port, subnet_ip=subnet_ip, subnet_mask=subnet_mask, ev=ev),
        }