"""
Basic Conformance test cases

Test cases in other modules depend on this functionality.
"""

import logging
from florence import config
import florence.controller_role_setup as role_setup
import florence.malformed_message as malformed_message
import oftest.base_tests as base_tests
import ofp
import oftest.testutils as testutils


class SetupDataPlane(base_tests.SimpleDataPlane):
    def setUp(self):
        base_tests.SimpleDataPlane.setUp(self)
        testutils.delete_all_flows(self.controller)
        testutils.delete_all_groups(self.controller)


class PortRange(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects the use of ports that are greater than
    OFPP_MAX and are not part of the reserved ports.
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


class TableId(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects the use of invalid table id.
    """
    def runTest(self):
        in_port, out_port1 = testutils.openflow_ports(2)

        testutils.delete_all_flows(self.controller)

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


class GroupId(SetupDataPlane):
    """
    Verify that the switch rejects the use of groups that are greater than
    OFPG_MAX and are not part of the reserved groups.
    """
    def runTest(self):
        port1, = testutils.openflow_ports(1)

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


class MeterId(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects the use of meters that are greater than
    OFPM_MAX and are not part of the virtual meters.
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


class TableLoop(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects the use of invalid Goto table id
    requesting a table loop.
    """
    def runTest(self):
        in_port, out_port1 = testutils.openflow_ports(2)

        testutils.delete_all_flows(self.controller)

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


class UnsupportedMessageType(base_tests.SimpleProtocol):
    """
    Verify that the switch throws an error when it receives a control message
    with unsupported message type.
    """
    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=4, type=97)

        reply, pkt = self.controller.transact(request)
        self.assertTrue(reply is not None,
                        "No response to malformed message type")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BAD_TYPE,
                        "reply error code is not bad type")


class UnsupportedVersionNumber(base_tests.SimpleProtocol):
    """
    Verify that the switch throws an error when it receives a connection setup
    message with an unsupported version number.
    """
    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=5, type=10)

        reply, pkt = self.controller.transact(request)
        self.assertTrue(reply is not None,
                        "No response to malformed message version")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BAD_VERSION,
                        "reply error code is not bad type")


class MalformedVersionNumber(base_tests.SimpleProtocol):
    """
    Verify that the switch throws an error when it receives a malformed
    version number after establishing connection between switch and
    controller with a different version.
    """
    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=0, type=0)

        reply, pkt = self.controller.transact(request)
        self.assertTrue(reply is not None, "No response to unsupported hello")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPET_HELLO_FAILED,
                        "reply error code is not bad type")


class InvalidOXMType(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a flow mod message
    with invalid OXM type.
    """
    def runTest(self):
        in_port, out_port1 = testutils.openflow_ports(2)

        testutils.delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        inst = ofp.instruction.apply_actions([ofp.action.output(out_port1)])
        logging.info("Inserting flow with malformed control message type")
        # Wrong type in flow mod
        request = ofp.message.flow_add(table_id=10,
                                       type=16,
                                       match=match,
                                       instructions=[inst],
                                       hard_timeout=1000)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None,
                        "No response to malformed control message type")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPFMFC_BAD_COMMAND,
                        "reply error code is not bad timeout")


class InvalidOXMLength(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a flow mod message
    with invalid OXM length.
    """
    def runTest(self):
        in_port, out_port1 = testutils.openflow_ports(2)

        testutils.delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        action = ofp.action.output(out_port1)
        inst = ofp.instruction.apply_actions(actions=[action])
        logging.info("Inserting flow with bad match length")
        # Wrong length in flow mod
        request = ofp.message.flow_add(table_id=10,
                                       match=match,
                                       instructions=[inst],
                                       hard_timeout=1000,
                                       length=10000)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to bad match length")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_MATCH,
                        "reply error type is not bad match request")
        self.assertTrue(reply.code == ofp.OFPBMC_BAD_LEN,
                        "reply error code is not bad match length")


class InvalidOXMValue(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a flow mod message
    with invalid message value
    """
    def runTest(self):
        in_port, out_port1 = testutils.openflow_ports(2)

        testutils.delete_all_flows(self.controller)

        match = ofp.match([ofp.oxm.in_port(in_port),
                          ofp.oxm.eth_type(0x800),
                          ofp.oxm.ip_dscp(100), ])
        action = ofp.action.output(out_port1)
        inst = ofp.instruction.apply_actions(actions=[action])
        logging.info("Inserting flow with bad match value")
        # Wrong match value in flow mod
        request = ofp.message.flow_add(table_id=10,
                                       match=match,
                                       instructions=[inst],
                                       hard_timeout=1000,)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to bad match value")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_MATCH,
                        "reply error type is not bad match request")
        self.assertTrue(reply.code == ofp.OFPBMC_BAD_VALUE,
                        "reply error code is not bad match value")


class DisabledTableFeatureRequest(base_tests.SimpleProtocol):
    """
    If the switch has disabled the table feature request with non-empty body,
    verify that the switch rejects this non-empty OFPMP_TABLE_FEATURES request
    with a permission error
    """
    pass


class HandshakeWithoutHello(base_tests.Handshake):
    """
    Check if the control connection is disconnected if the hello message
    is not exchanged within the specified default timeout.
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
    In the main connection between switch and controller, check if the switch
    processes a control message before exchanging OpenFlow hello message
    (connection establishment).
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


class MalformedHelloAfterConnection(base_tests.Handshake):
    """
    Verify that the switch will properly handle the abnormal condition,
    when it receives an OFPT_ERROR message with a type field of
    OFPET_HELLO_FAILED, a code field of OFPHFC_INCOMPATIBLE after establishing
    connection between switch and controller with a both agreed version.
    """
    def runTest(self):
        logging.info("Running " + str(self))
        self.controllerSetup(config["controller_host"],
                             config["controller_port"])
        self.controllers[0].connect(self.default_timeout)

        logging.info("Connected to switch" +
                     str(self.controllers[0].switch_addr))
        self.controllers[0].message_send(ofp.message.hello())
        request = ofp.message.hello_failed_error_msg(code=0)
        reply, pkt = self.controllers[0].transact(request,
                                                  self.default_timeout)
        self.assertTrue(reply is None,
                        """Response received for incompatible hello. """
                        """Requested not rejected or connection not closed""")


class CorruptedCookieValue(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a corrupted cookie
    value in OpenFlow messages after establishing connection between switch
    and controller.
    """
    def runTest(self):
        in_port, out_port1 = testutils.openflow_ports(2)
        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        inst = ofp.instruction.apply_actions([ofp.action.output(out_port1)])
        logging.info("Inserting flow with malformed/reserved cookie value")
        # Wrong type in flow mod
        request = ofp.message.flow_add(table_id=1,
                                       match=match,
                                       instructions=[inst],
                                       buffer_id=ofp.OFP_NO_BUFFER,
                                       cookie=0xfffffffffffffff,)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None,
                        "No response to malformed cookie value")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_FLOW_MOD_FAILED,
                        "reply error type is not flow mod failed")
        self.assertTrue(reply.code == ofp.OFPFMFC_UNKNOWN,
                        "reply error code is not unknown code type")


class MalformedBufferIDValue(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a malformed
    buffer ID value after establishing connection between switch & controller.
    """
    def runTest(self):
        in_port, out_port1 = testutils.openflow_ports(2)
        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        inst = ofp.instruction.apply_actions([ofp.action.output(out_port1)])
        logging.info("Inserting flow with malformed/reserved buffered value")
        # Wrong type in flow mod
        request = ofp.message.flow_add(table_id=1,
                                       match=match,
                                       instructions=[inst],
                                       buffer_id=1243,)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None,
                        "No response to malformed cookie value")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp. OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BUFFER_UNKNOWN,
                        "reply error code is not unknown buffer code")


class SlaveControllerViolation(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects unsupported control messages
    (OFPT_PACKET_OUT, OFPT_FLOW_MOD, OFPT_GROUP_MOD, OFPT_PORT_MOD,
    OFPT_TABLE_MOD requests, and OFPMP_TABLE_FEATURES)
    from slave controllers.
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
        testutils.do_barrier(self.controller)

        err_count = 0
        while self.controller.packets:
            msg = self.controller.packets.pop(0)[0]
            if msg.type == ofp.OFPT_ERROR:
                self.assertEquals(msg.err_type, ofp.OFPET_BAD_REQUEST)
                self.assertEquals(msg.code, ofp.OFPBRC_EPERM)
                err_count += 1

        self.assertEquals(err_count, 5, "Expected errors for each message")


class CorruptedGenerationID(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects role request message with
    stale generation id.
    """
    def runTest(self):
        role, gen = role_setup.request(self, ofp.OFPCR_ROLE_NOCHANGE)
        role_setup.error(self, ofp.OFPCR_ROLE_MASTER, gen-1, ofp.OFPRRFC_STALE)

        role1, gen1 = role_setup.request(self, ofp.OFPCR_ROLE_NOCHANGE)
        role_setup.error(self, ofp.OFPCR_ROLE_SLAVE, gen1-1, ofp.OFPRRFC_STALE)



class AuxConnectionTermination(base_tests.SimpleProtocol):
    """
    Verify that the auxiliary connection to the switch is terminated when the
    main connection to the switch is either broken/down.
    """
    pass


class AuxConnectionNonHello(base_tests.SimpleProtocol):
    """
    Verify that the switch rejects connection initiation with non-hello message
    in an auxiliary connection.
    """
    pass


class AuxConnectionUnsupportedMsg(base_tests.SimpleProtocol):
    """
    Verify that switch rejects unsupported messages in auxiliary connection.
    """
    pass
