# Florence: SDN Security Testing Framework

---

# Introduction

Florence is a security testing framework with set of tools and test
cases to validate SDN switch and controller implementations. While the
initial set of security test cases are specific to OpenFlow, the
framework can be extended to build complex test case scenarios.

Currently, florence can:
* Connect to a OpenFlow switch and generate security tests to validate
  the secureness and implementation robustness of the switch.
* Uses OpenFlow 1.3.5 version as the reference specification
* Connects to OpenvSwitch

Please check [ROADMAP](ROADMAP.md) for our upcoming features.

---

# Installation

Get the source:
```sh
$ git clone https://github.com/opennetworkingfoundation/florence
```

Install dependencies:
```sh
$ cd <florence>
$ pip install -r requirements.txt
```

---

# Quick Start

florence expects the switch to attempt connecting to a controller. The
default OpenFlow port (6653) is used in our setup.

Testing with OpenvSwitch:

Setup:
```sh
$ ./script/ovs-setup.sh
```

Configure OVS:
```sh
$ python ./script/ovs-ctl.py --config-file ./script/ovs-ctl.conf
```

Running Tests:

```sh
$ cd <florence>
$ sudo ./florence --help
```

To run the entire set of test cases:
```sh
$ ./florence
```

To determine how the switch handles malformed control messages:
```sh
$ ./florence malformed
```

To determine how the switch handles control message violations:
```sh
$ ./florence violations
```

To run a specific test case:
```sh
$ ./florence violations.TableLoop
```

---

# Participating


You can contribute to florence in mulitple ways:
* Code fixes via pull requests are welcome.
* Join the discussion by registering at https://groups.opensourcesdn.org/wg/FLORENCE/dashboard
* For comments, questions, suggestions, please contact us at florence@groups.opensourcesdn.org

---

# Notes

florence is a fork of [OFTest](https://github.com/floodlight/oftest)
and uses it as a library to build new security test cases. While the
initial codebase leverages some of the core functionalities of OFTest,
our plan is to extend florence to test the controller solutions and
additional southbound interfaces as well.

---
