"""
Basic Conformance test cases

Test cases in other modules depend on this functionality.
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
from oftest.testutils import *


class GroupTest(base_tests.SimpleDataPlane):
    def setUp(self):
        base_tests.SimpleDataPlane.setUp(self)
        delete_all_flows(self.controller)
        delete_all_groups(self.controller)

class TableIdViolation(base_tests.SimpleDataPlane):
    """
    Verify bad request error
    """
    def runTest(self):
        in_port, out_port1 = openflow_ports(2)

        delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        priority = 10

        logging.info("Inserting flow with bad table ID")
        request = ofp.message.flow_add(
                table_id=255,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions([ofp.action.output(out_port1)])
                ],
                buffer_id=ofp.OFP_NO_BUFFER,
                priority=priority,
                flags=ofp.OFPFF_SEND_FLOW_REM)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to malformed table ID")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        self.assertTrue(reply.err_type == ofp.OFPET_FLOW_MOD_FAILED,
                        "reply error type is not flow mod failed")
        self.assertTrue(reply.code == ofp.OFPFMFC_BAD_TABLE_ID,
                        "reply error code is not bad table id")

class TableLoopViolation(base_tests.SimpleDataPlane):
    """
    Verify table loop error
    """
    def runTest(self):
        in_port, out_port1 = openflow_ports(2)

        delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        priority = 1000

        logging.info("Inserting flow with bad goto table instruction")
        request = ofp.message.flow_add(
                table_id=10,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions([ofp.action.output(out_port1)]),
                    ofp.instruction.goto_table(5),
                ],
                buffer_id=ofp.OFP_NO_BUFFER,
                priority=priority,
                flags=ofp.OFPFF_SEND_FLOW_REM)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to table loop error")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_INSTRUCTION,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBIC_BAD_TABLE_ID,
                        "reply error code is not bad table id")

class GroupIdViolation(GroupTest):
    """
    Test cases to evaluate group ID violation
    """

    def runTest(self):
        port1, = openflow_ports(1)

        msg = ofp.message.group_add(
            group_type=ofp.OFPGT_ALL,
            group_id=ofp.OFPG_MAX+1,
            buckets=[
                ofp.bucket(actions=[ofp.action.output(port1)])])
	logging.info("Sending group add request")
        reply, pkt = self.controller.transact(msg)
        self.assertTrue(reply is not None, "No response to group add request")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        logging.info(reply.code)
        self.assertTrue(reply.err_type == ofp.OFPET_GROUP_MOD_FAILED,
                        "reply error type is not bad group mod request")
        self.assertTrue(reply.code == ofp.OFPGMFC_INVALID_GROUP,
                        "reply code is not invalid group")

class PortRangeViolation(base_tests.SimpleDataPlane):
    """
    Verify Port Range Violation
    """
    def runTest(self):
        logging.info("Testing for bad port modification message")
        request = ofp.message.port_mod(
                port_no=ofp.OFPP_ANY,)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to bad port mod")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        logging.info(reply.code)
        self.assertTrue(reply.err_type == ofp.OFPET_PORT_MOD_FAILED,
                        "reply error type is not bad port mod")
        self.assertTrue(reply.code == ofp.OFPPMFC_BAD_PORT,
                        "reply error code is not bad port")
