import sys
sys.path.append('../../../src/python/oftest/protocol')
from message import *
from action import *
from error import *
from class_maps import *

ofmsg_class_map_to_parents = {
    action_enqueue                     : [ofp_action_enqueue],
    action_output                      : [ofp_action_output],
    action_set_dl_dst                  : [ofp_action_dl_addr],
    action_set_dl_src                  : [ofp_action_dl_addr],
    action_set_nw_dst                  : [ofp_action_nw_addr],
    action_set_nw_src                  : [ofp_action_nw_addr],
    action_set_nw_tos                  : [ofp_action_nw_tos],
    action_set_tp_dst                  : [ofp_action_tp_port],
    action_set_tp_src                  : [ofp_action_tp_port],
    action_set_vlan_pcp                : [ofp_action_vlan_pcp],
    action_set_vlan_vid                : [ofp_action_vlan_vid],
    action_strip_vlan                  : [ofp_action_header],
    action_vendor                      : [ofp_action_vendor_header],
    aggregate_stats_entry              : [],
    aggregate_stats_reply              : [ofp_stats_reply],
    aggregate_stats_request            : [ofp_stats_request,
                                          ofp_aggregate_stats_request],
    bad_action_error_msg               : [ofp_error_msg],
    bad_request_error_msg              : [ofp_error_msg],
    barrier_reply                      : [],
    barrier_request                    : [],
    desc_stats_entry                   : [],
    desc_stats_reply                   : [ofp_stats_reply],
    desc_stats_request                 : [ofp_stats_request,
                                          ofp_desc_stats_request],
    echo_reply                         : [],
    echo_request                       : [],
    error                              : [ofp_error_msg],
    features_reply                     : [ofp_switch_features],
    features_request                   : [],
    flow_mod                           : [ofp_flow_mod],
    flow_mod_failed_error_msg          : [ofp_error_msg],
    flow_removed                       : [ofp_flow_removed],
    flow_stats_entry                   : [ofp_flow_stats],
    flow_stats_reply                   : [ofp_stats_reply],
    flow_stats_request                 : [ofp_stats_request,
                                          ofp_flow_stats_request],
    get_config_reply                   : [ofp_switch_config],
    get_config_request                 : [],
    hello                              : [],
    hello_failed_error_msg             : [ofp_error_msg],
    packet_in                          : [ofp_packet_in],
    packet_out                         : [ofp_packet_out],
    port_mod                           : [ofp_port_mod],
    port_mod_failed_error_msg          : [ofp_error_msg],
    port_stats_entry                   : [],
    port_stats_reply                   : [ofp_stats_reply],
    port_stats_request                 : [ofp_stats_request,
                                          ofp_port_stats_request],
    port_status                        : [ofp_port_status],
    queue_get_config_reply             : [ofp_queue_get_config_reply],
    queue_get_config_request           : [ofp_queue_get_config_request],
    queue_op_failed_error_msg          : [ofp_error_msg],
    queue_stats_entry                  : [],
    queue_stats_reply                  : [ofp_stats_reply],
    queue_stats_request                : [ofp_stats_request,
                                          ofp_queue_stats_request],
    set_config                         : [ofp_switch_config],
    stats_reply                        : [ofp_stats_reply],
    stats_request                      : [ofp_stats_request],
    table_stats_entry                  : [],
    table_stats_reply                  : [ofp_stats_reply],
    table_stats_request                : [ofp_stats_request,
                                          ofp_table_stats_request],
    vendor                             : [ofp_vendor_header]
}

ofmsg_names = {
    action_enqueue                     : 'action_enqueue',
    action_output                      : 'action_output',
    action_set_dl_dst                  : 'action_set_dl_dst',
    action_set_dl_src                  : 'action_set_dl_src',
    action_set_nw_dst                  : 'action_set_nw_dst',
    action_set_nw_src                  : 'action_set_nw_src',
    action_set_nw_tos                  : 'action_set_nw_tos',
    action_set_tp_dst                  : 'action_set_tp_dst',
    action_set_tp_src                  : 'action_set_tp_src',
    action_set_vlan_pcp                : 'action_set_vlan_pcp',
    action_set_vlan_vid                : 'action_set_vlan_vid',
    action_strip_vlan                  : 'action_strip_vlan',
    action_vendor                      : 'action_vendor',
    aggregate_stats_entry              : 'aggregate_stats_entry',
    aggregate_stats_reply              : 'aggregate_stats_reply',
    aggregate_stats_request            : 'aggregate_stats_request',
    bad_action_error_msg               : 'bad_action_error_msg',
    bad_request_error_msg              : 'bad_request_error_msg',
    barrier_reply                      : 'barrier_reply',
    barrier_request                    : 'barrier_request',
    desc_stats_entry                   : 'desc_stats_entry',
    desc_stats_reply                   : 'desc_stats_reply',
    desc_stats_request                 : 'desc_stats_request',
    echo_reply                         : 'echo_reply',
    echo_request                       : 'echo_request',
    error                              : 'error',
    features_reply                     : 'features_reply',
    features_request                   : 'features_request',
    flow_mod                           : 'flow_mod',
    flow_mod_failed_error_msg          : 'flow_mod_failed_error_msg',
    flow_removed                       : 'flow_removed',
    flow_stats_entry                   : 'flow_stats_entry',
    flow_stats_reply                   : 'flow_stats_reply',
    flow_stats_request                 : 'flow_stats_request',
    get_config_reply                   : 'get_config_reply',
    get_config_request                 : 'get_config_request',
    hello                              : 'hello',
    hello_failed_error_msg             : 'hello_failed_error_msg',
    ofp_desc_stats_request             : 'ofp_desc_stats_request',
    ofp_table_stats_request            : 'ofp_table_stats_request',
    packet_in                          : 'packet_in',
    packet_out                         : 'packet_out',
    port_mod                           : 'port_mod',
    port_mod_failed_error_msg          : 'port_mod_failed_error_msg',
    port_stats_entry                   : 'port_stats_entry',
    port_stats_reply                   : 'port_stats_reply',
    port_stats_request                 : 'port_stats_request',
    port_status                        : 'port_status',
    queue_get_config_reply             : 'queue_get_config_reply',
    queue_get_config_request           : 'queue_get_config_request',
    queue_op_failed_error_msg          : 'queue_op_failed_error_msg',
    queue_stats_entry                  : 'queue_stats_entry',
    queue_stats_reply                  : 'queue_stats_reply',
    queue_stats_request                : 'queue_stats_request',
    set_config                         : 'set_config',
    stats_reply                        : 'stats_reply',
    stats_request                      : 'stats_request',
    table_stats_entry                  : 'table_stats_entry',
    table_stats_reply                  : 'table_stats_reply',
    table_stats_request                : 'table_stats_request',
    vendor                             : 'vendor'
}

stats_entry_types = [
    aggregate_stats_entry,
    desc_stats_entry,
    port_stats_entry,
    queue_stats_entry,
    table_stats_entry
]

##@var A list of all OpenFlow messages including subtyped messages
of_messages = [
    aggregate_stats_reply,
    aggregate_stats_request,
    bad_action_error_msg,
    bad_request_error_msg,
    barrier_reply,
    barrier_request,
    desc_stats_reply,
    desc_stats_request,
    echo_reply,
    echo_request,
    features_reply,
    features_request,
    flow_mod,
    flow_mod_failed_error_msg,
    flow_removed,
    flow_stats_reply,
    flow_stats_request,
    get_config_reply,
    get_config_request,
    hello,
    hello_failed_error_msg,
    packet_in,
    packet_out,
    port_mod,
    port_mod_failed_error_msg,
    port_stats_reply,
    port_stats_request,
    port_status,
    queue_get_config_reply,
    queue_get_config_request,
    queue_op_failed_error_msg,
    queue_stats_reply,
    queue_stats_request,
    set_config,
    table_stats_reply,
    table_stats_request,
    vendor
]

# header_fields = ['version', 'xid']
# fixed_header_fields = ['type', 'length']

all_objs = ofmsg_class_map_to_parents.keys()
all_objs.sort()