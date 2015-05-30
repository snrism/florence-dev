"""
Malformed control message test cases

"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp

import florence.malformed_message as malformed_message

from oftest.testutils import *

@group('smoke')
class Hello(base_tests.SimpleProtocol):
    """
    Send a handshake request with the version not supported by the switch
    """

    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=0, type=0)

        reply, pkt = self.controller.transact(request)
        logging.info(repr(pkt))
        self.assertTrue(reply is not None, "No response to malformed hello")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPET_HELLO_FAILED,
                        "reply error code is not bad type")

@group('smoke')
class HeaderType(base_tests.SimpleProtocol):
    """
    Send a message with a bad type and verify an error is returned
    """

    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=4, type=97)

        reply, pkt = self.controller.transact(request)
        logging.info(repr(pkt))
        self.assertTrue(reply is not None, "No response to malformed message type")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BAD_TYPE,
                        "reply error code is not bad type")

@group('smoke')
class Version(base_tests.SimpleProtocol):
    """
    Send a message with a bad version and verify an error is returned
    """

    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=5, type=10)

        reply, pkt = self.controller.transact(request)
        logging.info(repr(pkt))
        self.assertTrue(reply is not None, "No response to malformed message version")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BAD_VERSION,
                        "reply error code is not bad type")

class MessageType(base_tests.SimpleDataPlane):
    """
    Verify malformed control type
    """
    def runTest(self):
        in_port, out_port1 = openflow_ports(2)

        delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        priority = 10

        logging.info("Inserting flow with malformed control message type")
        # Wrong type in flow mod
	request = ofp.message.flow_add(
                table_id=10,
		type=16,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions([ofp.action.output(out_port1)]),
                ],
                hard_timeout=1000)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to malformed control message type")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPFMFC_BAD_COMMAND,
                        "reply error code is not bad timeout")

class MessageLength(base_tests.SimpleDataPlane):
    """
    Verify malformed message length 
    """
    def runTest(self):
        in_port, out_port1 = openflow_ports(2)

        delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        priority = 10

        logging.info("Inserting flow with bad match length")
        # Wrong length in flow mod
        request = ofp.message.flow_add(
                table_id=10,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions(actions=[ofp.action.output(out_port1)]),
                ],
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
