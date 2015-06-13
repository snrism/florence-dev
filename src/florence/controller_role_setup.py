"""
Controller role setup helper functions from OFTest
"""
import ofp


def add_mod64(a, b):
    return (a + b) & (2**64-1)


def request(test, role, gen=None, con=None):
    """
    Send a role request we expect to succeed
    """
    if con is None:
        con = test.controller
    request = ofp.message.role_request(role=role, generation_id=gen)
    response, _ = con.transact(request)
    test.assertTrue(isinstance(response, ofp.message.role_reply),
                    "Expected a role reply")
    if role != ofp.OFPCR_ROLE_NOCHANGE:
        test.assertEquals(response.role, role)
    if gen is not None:
        test.assertEquals(response.generation_id, gen)
    return response.role, response.generation_id


def error(test, role, gen, code, con=None):
    """
    Send a bad role request
    """
    if con is None:
        con = test.controller
    request = ofp.message.role_request(role=role, generation_id=gen)
    response, _ = con.transact(request)
    test.assertIsInstance(response, ofp.message.role_request_failed_error_msg)
    test.assertEqual(response.code, code)
