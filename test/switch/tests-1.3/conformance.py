# Distributed under the OpenFlow Software License (see LICENSE)
# Copyright (c) 2010 The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012, 2013 Big Switch Networks, Inc.
# Copyright (c) 2012, 2013 CPqD
# Copyright (c) 2012, 2013 Ericsson
"""
Basic Conformance test cases

Test cases in other modules depend on this functionality.
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp

import florence.malformed_message as malformed_message

from oftest.testutils import *

@group('smoke')
class MalformedHello(base_tests.SimpleProtocol):
    """
    Send a handshake request with the version not supported by the switch
    """

    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=0, type=0)

        reply, pkt = self.controller.transact(request)
        logging.info(repr(pkt))
        self.assertTrue(reply is not None, "No response to malformed hellow")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPET_HELLO_FAILED,
                        "reply error code is not bad type")

@group('smoke')
class MalformedHeaderType(base_tests.SimpleProtocol):
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
class MalformedVersion(base_tests.SimpleProtocol):
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

@group('smoke')
class MalformedHeaderLength(base_tests.SimpleProtocol):
    """
    Send a message with a bad length and verify an error is returned
    """

    def runTest(self):
        logging.info("Running " + str(self))
        request = malformed_message.malformed_message(version=4, type=1, length=10)

        reply, pkt = self.controller.transact(request)
        logging.info(repr(pkt))
        self.assertTrue(reply is not None, "No response to malformed message length")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.err_type)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BAD_VERSION,
                        "reply error code is not bad type")

class MalformedTableID(base_tests.SimpleDataPlane):
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

class MalformedControlType(base_tests.SimpleDataPlane):
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

class BadExperimenterId(base_tests.SimpleDataPlane):
    """
    Verify table loop error
    """
    def runTest(self):

        logging.info("Generating Bad Experimenter Id")
        request = ofp.message.experimenter_error_msg(
                experimenter=65535
                )
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to bad experimenter id")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.code)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BAD_EXPERIMENTER,
                        "reply error code is not bad experimenter")

class BadExperimenterType(base_tests.SimpleDataPlane):
    """
    Verify table loop error
    """
    def runTest(self):

        logging.info("Generating Bad Experimenter Field")
        request = ofp.message.experimenter_error_msg(
                subtype=400,
		experimenter=0
                )
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to bad experimenter type")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        logging.info(reply.code)
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_REQUEST,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBRC_BAD_EXPERIMENTER,
                        "reply error code is not bad experimenter type")

class MalformedInstructionType(base_tests.SimpleDataPlane):
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

        logging.info("Inserting flow with malformed instruction type")
        # Wrong type in flow mod
        request = ofp.message.flow_add(
                table_id=10,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions(actions=[ofp.action.output(out_port1)], type=7),
                ],
                hard_timeout=1000)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to malformed control message type")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_INSTRUCTION,
                        "reply error type is not bad request")
        self.assertTrue(reply.code == ofp.OFPBIC_UNKNOWN_INST,
                        "reply error code is not bad timeout")

class DuplicateMatchField(base_tests.SimpleDataPlane):
    """
    Verify malformed control type
    """
    def runTest(self):
        in_port, out_port1 = openflow_ports(2)

        delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
	    ofp.oxm.in_port(4)
        ])
        priority = 10

        logging.info("Inserting flow with duplicate match field")
        # Wrong type in flow mod
        request = ofp.message.flow_add(
                table_id=10,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions(actions=[ofp.action.output(out_port1)], type=7),
                ],
                hard_timeout=1000)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to duplicate match field")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_MATCH,
                        "reply error type is not bad match request")
        self.assertTrue(reply.code == ofp.OFPBMC_DUP_FIELD,
                        "reply error code is not bad duplicate field")

class BadPreReqMatch(base_tests.SimpleDataPlane):
    """
    Verify malformed control type
    """
    def runTest(self):
        in_port, out_port1 = openflow_ports(2)

        delete_all_flows(self.controller)

        match = ofp.match([
            ofp.oxm.in_port(in_port),
	    ofp.oxm.ipv4_src(0xc0a80001),
            ofp.oxm.ipv4_dst(0xc0a80002),
        ])
        priority = 10

        logging.info("Inserting flow with bad pre-requisite")
        # Wrong type in flow mod
        request = ofp.message.flow_add(
                table_id=10,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions(actions=[ofp.action.output(out_port1)]),
                ],
                hard_timeout=1000)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to bad pre requisite")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_MATCH,
                        "reply error type is not bad match request")
        self.assertTrue(reply.code == ofp.OFPBMC_BAD_PREREQ,
                        "reply error code is not bad pre-requisite")

class BadMatchLength(base_tests.SimpleDataPlane):
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

        logging.info("Inserting flow with bad match length")
        # Wrong type in flow mod
        request = ofp.message.flow_add(
                table_id=10,
                match=match,
                instructions=[
                    ofp.instruction.apply_actions(actions=[ofp.action.output(out_port1)]),
                ],
                hard_timeout=1000,
		length=100)
        reply, pkt = self.controller.transact(request)

        self.assertTrue(reply is not None, "No response to bad match length")
        self.assertTrue(reply.type == ofp.OFPT_ERROR,
                        "reply not an error message")
        self.assertTrue(reply.err_type == ofp.OFPET_BAD_MATCH,
                        "reply error type is not bad match request")
        self.assertTrue(reply.code == ofp.OFPBMC_BAD_LEN,
                        "reply error code is not bad match length")
