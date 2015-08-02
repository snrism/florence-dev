"""
Basic Conformance test cases

Test cases in other modules depend on this functionality.
"""

import logging
from florence import config, Color
import florence.controller_role_setup as role_setup
import florence.malformed_message as malformed_message
import oftest.base_tests as base_tests
import ofp
import oftest.testutils as testutils
import sys


PASS = Color.PASS + "[PASS]" + Color.END
FAIL = Color.FAIL + "[FAIL]" + Color.END
INFO = Color.INFO + "[INFO]" + Color.END

# Logger to output test case results
log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(message)s'))
handler.setLevel(logging.INFO)
log.addHandler(handler)
log.setLevel(logging.INFO)


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
        log.info(INFO + " 1.1.10 - Port Range Violation")
        request = ofp.message.port_mod(port_no=ofp.OFPP_ANY,)
        reply, pkt = self.controller.transact(request)
        try:
            self.assertTrue(reply is not None,
                            "No response to bad port mod")
        except AssertionError:
            log.error(FAIL + " -> No response to bad port modification")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_PORT_MOD_FAILED,
                            "Reply error type is not bad port mod request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad port mod request")
        try:
            self.assertTrue(reply.code == ofp.OFPPMFC_BAD_PORT,
                           "Reply code is not bad port")
            log.info(PASS + " -> Port range violation rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not bad port")


class TableId(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects the use of invalid table id.
    """
    def runTest(self):
        log.info(INFO + " 1.1.20 - Table Identifier Violation")
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
        try:
            self.assertTrue(reply is not None,
                            "No response to malformed table ID")
        except AssertionError:
            log.error(FAIL + " -> No response to malformed table ID")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_FLOW_MOD_FAILED,
                            "Reply error type is not flow mod failed")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not flow mod failed")
        try:
            self.assertTrue(reply.code == ofp.OFPFMFC_BAD_TABLE_ID,
                           "Reply error code is not bad table ID")
            log.info(PASS + " -> Table ID violation rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not bad table ID")


class GroupId(SetupDataPlane):
    """
    Verify that the switch rejects the use of groups that are greater than
    OFPG_MAX and are not part of the reserved groups.
    """
    def runTest(self):
        log.info(INFO + " 1.1.30 - Group Identifier Violation")
        port1, = testutils.openflow_ports(1)

        msg = ofp.message.group_add(
            group_type=ofp.OFPGT_ALL,
            group_id=ofp.OFPG_ANY,
            buckets=[
                ofp.bucket(actions=[ofp.action.output(port1)])])
        logging.info("Sending group add request")
        reply, pkt = self.controller.transact(msg)
        try:
            self.assertTrue(reply is not None,
                            "No response to group add request")
        except AssertionError:
            log.error(FAIL + " -> No response to group add request")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_GROUP_MOD_FAILED,
                            "Reply error type is not bad group mod request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad group mod request")
        try:
            self.assertTrue(reply.code == ofp.OFPGMFC_INVALID_GROUP,
                           "Reply code is not invalid group")
            log.info(PASS + " -> Group Identifier violation rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not invalid group")


class MeterId(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects the use of meters that are greater than
    OFPM_MAX and are not part of the virtual meters.
    """
    def runTest(self):
        log.info(INFO + " 1.1.40 - Meter Identifier Violation")
        request = ofp.message.meter_mod(meter_id=ofp.OFPM_ALL,)
        reply, pkt = self.controller.transact(request)
        try:
            self.assertTrue(reply is not None,
                            "No response to bad meter mod")
        except AssertionError:
            log.error(FAIL + " -> No response to bad meter modification")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_METER_MOD_FAILED,
                            "Reply error type is not bad meter mod")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad meter mod request")
        try:
            self.assertTrue(reply.code == ofp.OFPMMFC_INVALID_METER,
                           "Reply code is not invalid meter")
            log.info(PASS + " -> Meter ID violation rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not invalid meter")


class TableLoop(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects the use of invalid Goto table id
    requesting a table loop.
    """
    def runTest(self):
        log.info(INFO + " 1.1.50 - Table Loop Violation")
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
        try:
            self.assertTrue(reply is not None,
                            "No response to table loop error")
        except AssertionError:
            log.error(FAIL + " -> No response to table loop error")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_INSTRUCTION,
                            "Reply error type is not bad instruction request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad instruction request")
        try:
            self.assertTrue(reply.code == ofp.OFPBIC_BAD_TABLE_ID,
                           "Reply error code is not bad table id")
            log.info(PASS + " -> Table Loop violation rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply error code is not bad table id")


class UnsupportedMessageType(base_tests.SimpleProtocol):
    """
    Verify that the switch throws an error when it receives a control message
    with unsupported message type.
    """
    def runTest(self):
        log.info(INFO + " 1.1.60 - Unsupported Message Type")
        request = malformed_message.malformed_message(version=4, type=97)

        reply, pkt = self.controller.transact(request)
        try:
            self.assertTrue(reply is not None,
                            "No response to unsupported message type")
        except AssertionError:
            log.error(FAIL + " -> No response to unsupported message type")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                            "Reply error type is not bad request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad request")
        try:
            self.assertTrue(reply.code == ofp.OFPBRC_BAD_TYPE,
                           "Reply error code is not bad type")
            log.info(PASS + " -> Unsupported message type rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not bad type")


class UnsupportedVersionNumber(base_tests.SimpleProtocol):
    """
    Verify that the switch throws an error when it receives a connection setup
    message with an unsupported version number.
    """
    def runTest(self):
        log.info(INFO + " 1.1.70 - Unsupported Version Number")
        request = malformed_message.malformed_message(version=5, type=10)

        reply, pkt = self.controller.transact(request)
        try:
            self.assertTrue(reply is not None,
                            "No response to unsupported version number")
        except AssertionError:
            log.error(FAIL + " -> No response to unsupported version number")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                            "Reply error type is not bad request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad request")
        try:
            self.assertTrue(reply.code == ofp.OFPBRC_BAD_VERSION,
                           "Reply error code is not bad version")
            log.info(PASS + " -> Unsupported version number rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not bad version")


class MalformedVersionNumber(base_tests.SimpleProtocol):
    """
    Verify that the switch throws an error when it receives a malformed
    version number after establishing connection between switch and
    controller with a different version.
    """
    def runTest(self):
        log.info(INFO + " 1.1.80 - Malformed Version Number")
        request = malformed_message.malformed_message(version=0, type=0)

        reply, pkt = self.controller.transact(request)
        try:
            self.assertTrue(reply is not None,
                            "No response to malformed version number")
        except AssertionError:
            log.error(FAIL + " -> No response to malformed version number")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                            "Reply error type is not bad request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad request")
        try:
            self.assertTrue(reply.code == ofp.OFPET_HELLO_FAILED,
                           "Reply error code is not hello failed")
            log.info(PASS + " -> Malformed version number rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not hello failed")


class InvalidOXMType(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a flow mod message
    with invalid OXM type.
    """
    def runTest(self):
        log.info(INFO + " 1.1.90 - Invalid OXM – Type")
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
        try:
            self.assertTrue(reply is not None,
                            "No response to invalid OXM type")
        except AssertionError:
            log.error(FAIL + " -> No response to invalid OXM type")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                            "Reply error type is not bad request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad request")
        try:
            self.assertTrue(reply.code == ofp.OFPFMFC_BAD_COMMAND,
                           "Reply error code is not bad command")
            log.info(PASS + " -> Invalid OXM type rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not bad command")


class InvalidOXMLength(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a flow mod message
    with invalid OXM length.
    """
    def runTest(self):
        log.info(INFO + " 1.1.100 - Invalid OXM – Length")
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
        try:
            self.assertTrue(reply is not None,
                            "No response to invalid OXM length")
        except AssertionError:
            log.error(FAIL + " -> No response to invalid OXM length")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_MATCH,
                            "Reply error type is not bad match request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad match request")
        try:
            self.assertTrue(reply.code == ofp.OFPBMC_BAD_LEN,
                           "Reply error code is not bad match length")
            log.info(PASS + " -> Invalid OXM length rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not bad match length")


class InvalidOXMValue(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a flow mod message
    with invalid message value
    """
    def runTest(self):
        log.info(INFO + " 1.1.110 - Invalid OXM – Value")
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
        try:
            self.assertTrue(reply is not None,
                            "No response to invalid OXM value")
        except AssertionError:
            log.error(FAIL + " -> No response to invalid OXM value")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_MATCH,
                            "Reply error type is not bad match request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad match request")
        try:
            self.assertTrue(reply.code == ofp.OFPBMC_BAD_VALUE,
                           "Reply error code is not bad match value")
            log.info(PASS + " -> Invalid OXM value rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply code is not bad match value")


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
        log.info(INFO + " 1.1.130 - Handshake without Hello Message")
        self.controllerSetup(config["controller_host"],
                             config["controller_port"])
        self.controllers[0].connect(self.default_timeout)
        try:
            # wait for controller to die
            self.assertTrue(self.controllers[0].wait_disconnected(timeout=10),
                            "Not notified about controller disconnect")
            log.info(PASS + " -> Handshake without Hello rejected")
        except AssertionError:
            log.error(FAIL + " -> Not notified about controller disconnect")


class ControlMsgBeforeHello(base_tests.Handshake):
    """
    In the main connection between switch and controller, check if the switch
    processes a control message before exchanging OpenFlow hello message
    (connection establishment).
    """
    def runTest(self):
        log.info(INFO + " 1.1.140 - Control Message before Hello Message")
        self.controllerSetup(config["controller_host"],
                             config["controller_port"])
        self.controllers[0].connect(self.default_timeout)

        logging.info("Connected to switch" +
                     str(self.controllers[0].switch_addr))

        barrier_req = ofp.message.barrier_request()
        reply, pkt = self.controllers[0].transact(barrier_req,
                                                  self.default_timeout)
        try:
            self.assertTrue(reply is None,
                            "Got response to control message before Hello")
            log.info(PASS + " -> Control Message before Hello rejected")
        except AssertionError:
            log.error(FAIL + " -> Got response to control message"
                      + " before Hello")


class IncompatibleHelloAfterConnection(base_tests.Handshake):
    """
    Verify that the switch will properly handle the abnormal condition,
    when it receives an OFPT_ERROR message with a type field of
    OFPET_HELLO_FAILED, a code field of OFPHFC_INCOMPATIBLE after establishing
    connection between switch and controller with a both agreed version.
    """
    def runTest(self):
        log.info(INFO + " 1.1.150 - Incompatible Hello"
                 + " after Connection Establishment")
        self.controllerSetup(config["controller_host"],
                             config["controller_port"])
        self.controllers[0].connect(self.default_timeout)

        logging.info("Connected to switch" +
                     str(self.controllers[0].switch_addr))
        self.controllers[0].message_send(ofp.message.hello())
        request = ofp.message.hello_failed_error_msg(code=0)
        reply, pkt = self.controllers[0].transact(request,
                                                  self.default_timeout)
        try:
            self.assertTrue(reply is None,
                            """Response received for incompatible hello. """
                            """Request not rejected/connection not closed""")
            log.info(PASS + " -> Incompatible Hello After Connection rejected")
        except AssertionError:
            log.error(FAIL + " -> Request not rejected/connection not closed")


class CorruptedCookieValue(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a corrupted cookie
    value in OpenFlow messages after establishing connection between switch
    and controller.
    """
    def runTest(self):
        log.info(INFO + " 1.1.160 - Corrupted Cookie Values")
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
        try:
            self.assertTrue(reply is not None,
                            "No response to corrupted cookie value")
        except AssertionError:
            log.error(FAIL + " -> No response to corrupted cookie value")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_FLOW_MOD_FAILED,
                            "Reply error type is not flow mod failed")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not flow mod failed")
        try:
            self.assertTrue(reply.code == ofp.OFPFMFC_UNKNOWN,
                           "Reply error code is not unknown code type")
            log.info(PASS + " -> Corrupted Cookie value rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply error code is not unknown code type")


class MalformedBufferIDValue(base_tests.SimpleDataPlane):
    """
    Verify that the switch throws an error when it receives a malformed
    buffer ID value after establishing connection between switch & controller.
    """
    def runTest(self):
        log.info(INFO + " 1.1.170 - Malformed Buffer ID Values")
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
        try:
            self.assertTrue(reply is not None,
                            "No response to malformed cookie value")
        except AssertionError:
            log.error(FAIL + " -> No response to malformed cookie value")
        try:
            self.assertTrue(reply.type == ofp.OFPT_ERROR,
                            "Reply not an error message")
        except AssertionError:
            log.error(FAIL + " -> Reply not an error message")
        try:
            self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                            "Reply error type is not bad request")
        except AssertionError:
            log.error(FAIL + " -> Reply error type is not bad request")
        try:
            self.assertTrue(reply.code == ofp.OFPBRC_BUFFER_UNKNOWN,
                           "Reply error code is not unknown buffer code")
            log.info(PASS + " -> Malformed buffer ID value rejected")
        except AssertionError:
            log.error(FAIL + " -> Reply error code is not unknown buffer code")


class SlaveControllerViolation(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects unsupported control messages
    (OFPT_PACKET_OUT, OFPT_FLOW_MOD, OFPT_GROUP_MOD, OFPT_PORT_MOD,
    OFPT_TABLE_MOD requests, and OFPMP_TABLE_FEATURES)
    from slave controllers.
    """
    def runTest(self):
        log.info(INFO + " 1.2.10 - Slave Controller Violation")
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
        try:
            self.assertEquals(err_count, 5,
                              "Expected errors for each message")
            log.info(PASS + " -> Slave Controller violations rejected")
        except AssertionError:
            log.error(FAIL + " -> Slave controller violation processed")


class CorruptedGenerationID(base_tests.SimpleDataPlane):
    """
    Verify that the switch rejects role request message with
    stale generation id.
    """
    def runTest(self):
        log.info(INFO + " 1.2.20 - Corrupted Generation ID")
        role, gen = role_setup.request(self, ofp.OFPCR_ROLE_NOCHANGE)
        try:
            role_setup.error(self,
                             ofp.OFPCR_ROLE_MASTER,
                             gen-1,
                             ofp.OFPRRFC_STALE)
        except AssertionError:
            log.error(FAIL + " -> Corrupted Generation ID processed")

        role1, gen1 = role_setup.request(self, ofp.OFPCR_ROLE_NOCHANGE)
        try:
            role_setup.error(self,
                             ofp.OFPCR_ROLE_SLAVE,
                             gen1-1,
                             ofp.OFPRRFC_STALE)
            log.info(PASS + " -> Corrupted Generation ID rejected")
        except AssertionError:
            log.error(FAIL + " -> Corrupted Generation ID processed")


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
