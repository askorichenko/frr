#!/usr/bin/env python
# SPDX-License-Identifier: ISC

# Copyright (c) 2023 by
# Donatas Abraitis <donatas@opensourcerouting.org>
#

"""
Test if local-preference is passed between different EBGP peers when
EBGP-OAD is configured.

Also check if no-export community is passed to the EBGP-OAD peer.
"""

import os
import sys
import json
import pytest
import functools

pytestmark = [pytest.mark.bgpd]

CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(CWD, "../"))

# pylint: disable=C0413
from lib import topotest
from lib.topogen import Topogen, get_topogen


def setup_module(mod):
    topodef = {"s1": ("r1", "r2", "r4"), "s2": ("r2", "r3"), "s3": ("r4", "r5")}
    tgen = Topogen(topodef, mod.__name__)
    tgen.start_topology()

    router_list = tgen.routers()

    for _, (rname, router) in enumerate(router_list.items(), 1):
        router.load_frr_config(os.path.join(CWD, "{}/frr.conf".format(rname)))

    tgen.start_router()


def teardown_module(mod):
    tgen = get_topogen()
    tgen.stop_topology()


def test_bgp_oad():
    tgen = get_topogen()

    if tgen.routers_have_failure():
        pytest.skip(tgen.errors)

    r1 = tgen.gears["r1"]
    r2 = tgen.gears["r2"]
    r3 = tgen.gears["r3"]
    r4 = tgen.gears["r4"]
    r5 = tgen.gears["r5"]

    def _bgp_converge():
        output = json.loads(r1.vtysh_cmd("show bgp ipv4 unicast 10.10.10.10/32 json"))
        expected = {
            "paths": [
                {
                    "aspath": {"string": "65002 65003"},
                    "metric": 123,
                    "locPrf": 123,
                    "peer": {
                        "hostname": "r2",
                        "type": "external (oad)",
                    },
                },
                {
                    "aspath": {"string": "65004 65005"},
                    "metric": 123,
                    "locPrf": 123,
                    "bestpath": {"selectionReason": "Peer Type"},
                    "peer": {
                        "hostname": "r4",
                        "type": "external",
                    },
                },
            ]
        }
        return topotest.json_cmp(output, expected)

    test_func = functools.partial(
        _bgp_converge,
    )
    _, result = topotest.run_and_expect(test_func, None, count=30, wait=1)
    assert result is None, "Can't converge"

    def _bgp_check_no_export(router, arg=[{"valid": True}]):
        output = json.loads(router.vtysh_cmd("show bgp ipv4 unicast json"))
        expected = {
            "routes": {
                "10.10.10.1/32": arg,
            }
        }
        return topotest.json_cmp(output, expected)

    test_func = functools.partial(
        _bgp_check_no_export,
        r2,
    )
    _, result = topotest.run_and_expect(test_func, None, count=30, wait=1)
    assert result is None, "10.10.10.1/32 should be advertised to r2"

    test_func = functools.partial(
        _bgp_check_no_export,
        r3,
    )
    _, result = topotest.run_and_expect(test_func, None, count=30, wait=1)
    assert result is None, "10.10.10.1/32 should be advertised to r3"

    test_func = functools.partial(
        _bgp_check_no_export,
        r4,
        None,
    )
    _, result = topotest.run_and_expect(test_func, None, count=30, wait=1)
    assert result is None, "10.10.10.1/32 should not be advertised to r4 (not OAD peer)"

    def _bgp_check_non_transitive_extended_community(
        router, arg={"string": "LB:65003:12500000 (100.000 Mbps)"}
    ):
        output = json.loads(
            router.vtysh_cmd("show bgp ipv4 unicast 10.10.10.20/32 json")
        )
        expected = {
            "paths": [
                {
                    "extendedCommunity": arg,
                }
            ]
        }
        return topotest.json_cmp(output, expected)

    test_func = functools.partial(
        _bgp_check_non_transitive_extended_community,
        r4,
    )
    _, result = topotest.run_and_expect(test_func, None, count=30, wait=1)
    assert (
        result is None
    ), "10.10.10.20/32 should be received at r4 with non-transitive extended community"

    test_func = functools.partial(
        _bgp_check_non_transitive_extended_community, r5, None
    )
    _, result = topotest.run_and_expect(test_func, None, count=30, wait=1)
    assert (
        result is None
    ), "10.10.10.20/32 should NOT be received at r5 with non-transitive extended community"


if __name__ == "__main__":
    args = ["-s"] + sys.argv[1:]
    sys.exit(pytest.main(args))
