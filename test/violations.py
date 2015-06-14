"""
Basic Conformance test cases

Test cases in other modules depend on this functionality.
"""

import logging
from florence import config
import florence.controller_role_setup as role_setup
import oftest.base_tests as base_tests
import ofp
from oftest.testutils import *


class SetupDataPlane(base_tests.SimpleDataPlane):
    def setUp(self):
        base_tests.SimpleDataPlane.setUp(self)
        delete_all_flows(self.controller)
        delete_all_groups(self.controller)


class TableId(base_tests.SimpleDataPlane):
    """
    Verify bad Table ID request error
    """
    def runTest(self):
        in_port, out_port1 = openflow_ports(2)

        delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        priority = 10
        logging.info("Inserting flow with bad table ID")
        inst = ofp.instruction.apply_actions([ofp.action.output(out_port1)])
        request = ofp.message.flow_add(table_id=255,
                                       match=match,
                                       instructions=[inst],
                                       buffer_id=ofp.OFP_NO_BUFFER,
                                       priority=priority,
                                       flags=ofp.OFPFF_SEND_FLOW_REM)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None,
                        "No response to malformed table ID")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_FLOW_MOD_FAILED,
                        "reply error type is not flow mod failed")
        self.assertTrue(reply.code == ofp.OFPFMFC_BAD_TABLE_ID,
                        "reply error code is not bad table id")


class TableLoop(base_tests.SimpleDataPlane):
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
        inst1 = ofp.instruction.apply_actions([ofp.action.output(out_port1)])
        inst2 = ofp.instruction.goto_table(5)
        request = ofp.message.flow_add(table_id=10,
                                       match=match,
                                       instructions=[inst1, inst2],
                                       buffer_id=ofp.OFP_NO_BUFFER,
                                       priority=priority,
                                       flags=ofp.OFPFF_SEND_FLOW_REM)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None,
                        "No response to table loop error")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_INSTRUCTION,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBIC_BAD_TABLE_ID,
                        "reply error code is not bad table id")


class GroupId(SetupDataPlane):
    """
    Test cases to evaluate group ID violation
    """

    def runTest(self):
        port1, = openflow_ports(1)

        msg = ofp.message.group_add(
            group_type=ofp.OFPGT_ALL,
            group_id=ofp.OFPG_ANY,
            buckets=[
                ofp.bucket(actions=[ofp.action.output(port1)])])
        logging.info("Sending group add request")
        reply, pkt = self.controller.transact(msg)
        self.assertTrue(reply is not None,
                        "No response to group add request")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_GROUP_MOD_FAILED,
                        "reply error type is not bad group mod request")
        self.assertTrue(reply.code == ofp.OFPGMFC_INVALID_GROUP,
                        "reply code is not invalid group")


class PortRange(base_tests.SimpleDataPlane):
    """
    Verify Port Range Violation
    """
    def runTest(self):
        logging.info("Testing for bad port modification message")
        request = ofp.message.port_mod(port_no=ofp.OFPP_ANY,)
        reply, pkt = self.controller.transact(request)
        self.assertTrue(reply is not None,
                        "No response to bad port mod")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_PORT_MOD_FAILED,
                        "reply error type is not bad port mod")
        self.assertTrue(reply.code == ofp.OFPPMFC_BAD_PORT,
                        "reply error code is not bad port")


class MeterId(base_tests.SimpleDataPlane):
    """
    Verify Meter ID Violation
    """
    def runTest(self):
        logging.info("Testing for bad meter modification message")
        request = ofp.message.meter_mod(meter_id=ofp.OFPM_ALL,)
        reply, pkt = self.controller.transact(request)
        self.assertTrue(reply is not None,
                        "No response to bad meter mod")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_METER_MOD_FAILED,
                        "reply error type is not bad meter mod")
        self.assertTrue(reply.code == ofp.OFPMMFC_INVALID_METER,
                        "reply error code is not bad meter id")


class RolePermissions(base_tests.SimpleDataPlane):
    """
    Check for role permission errors when a
    slave connection modifies switch state
    """
    def runTest(self):

        role, gen = role_setup.request(self, ofp.OFPCR_ROLE_NOCHANGE)
        role_setup.request(self, ofp.OFPCR_ROLE_SLAVE, gen)

        # Generate requests not allowed in Slave Controller Role
        # Packet Out
        self.controller.message_send(
            ofp.message.packet_out(buffer_id=ofp.OFP_NO_BUFFER))

        # Flow Modification
        self.controller.message_send(
            ofp.message.flow_delete(
                buffer_id=ofp.OFP_NO_BUFFER,
                out_port=ofp.OFPP_ANY,
                out_group=ofp.OFPG_ANY))

        # Group Modification
        self.controller.message_send(
            ofp.message.group_mod(
                command=ofp.OFPGC_DELETE,
                group_id=ofp.OFPG_ALL))

        # Port Modification
        self.controller.message_send(
            ofp.message.port_mod(
                port_no=ofp.OFPP_MAX))

        # Table Modification
        self.controller.message_send(
            ofp.message.table_mod(
                table_id=1))

        # Since Table Features is unsupported in OF1.3, we skip it
        do_barrier(self.controller)

        err_count = 0
        while self.controller.packets:
            msg = self.controller.packets.pop(0)[0]
            if msg.type == ofp.OFPT_ERROR:
                self.assertEquals(msg.err_type, ofp.OFPET_BAD_REQUEST)
                self.assertEquals(msg.code, ofp.OFPBRC_EPERM)
                err_count += 1

        self.assertEquals(err_count, 5, "Expected errors for each message")


class GenerationID(base_tests.SimpleDataPlane):
    """
    Stale generation ID should be rejected
    """
    def runTest(self):
        role, gen = role_setup.request(self, ofp.OFPCR_ROLE_NOCHANGE)
        role_setup.error(self, ofp.OFPCR_ROLE_MASTER, gen-1, ofp.OFPRRFC_STALE)

        role1, gen1 = role_setup.request(self, ofp.OFPCR_ROLE_NOCHANGE)
        role_setup.error(self, ofp.OFPCR_ROLE_SLAVE, gen1-1, ofp.OFPRRFC_STALE)


class HandshakeWithoutHello(base_tests.Handshake):
    """
    Connect to switch without OpenFlow hello message,
    and wait for disconnect.
    """
    def runTest(self):
        self.controllerSetup(config["controller_host"],
                             config["controller_port"])
        self.controllers[0].connect(self.default_timeout)
        # wait for controller to die
        self.assertTrue(self.controllers[0].wait_disconnected(timeout=10),
                        "Not notified of controller disconnect")


class ControlMsgBeforeHello(base_tests.Handshake):
    """
    Establish connection and send contol message before hellow.
    """
    def runTest(self):
        self.controllerSetup(config["controller_host"],
                             config["controller_port"])
        self.controllers[0].connect(self.default_timeout)

        logging.info("Connected to switch" +
                     str(self.controllers[0].switch_addr))

        barrier_req = ofp.message.barrier_request()
        reply, pkt = self.controllers[0].transact(barrier_req,
                                                  self.default_timeout)
        self.assertTrue(reply is None,
                        "Got response to control message before Hello")
