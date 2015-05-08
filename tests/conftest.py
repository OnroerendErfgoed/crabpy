# -*- coding: utf-8 -*

import os
import pytest
from six.moves import configparser


def pytest_addoption(parser):
    parser.addoption(
        "--crab-integration",
        action="store_true",
        help="crab-integartion: Run CRAB integration tests or not?"
    )
    parser.addoption(
        "--capakey-integration",
        action="store_true",
        help="capakey-integartion: Run CAPAKEY integration tests or not?"
    )
    parser.addoption(
        "--capakey-user",
        action="store", default="capakey_user",
        help="capakey-user: Run CAPAKEY integration tests with this user"
    )
    parser.addoption(
        "--capakey-password",
        action="store", default="capakey_password",
        help="capakey-password: Run CAPAKEY integration tests with this password"
    )

@pytest.fixture(scope="session")
def capakey(request):
    if not request.config.getoption('--capakey-integration'):
        return None
    from crabpy.client import capakey_factory
    capakey = capakey_factory(
        user=request.config.getoption("--capakey-user"),
        password=request.config.getoption("--capakey-password")
    )
    return capakey

@pytest.fixture(scope="module")
def capakey_gateway(capakey):
    from crabpy.gateway.capakey import CapakeyGateway
    capakey_gateway = CapakeyGateway(
        capakey
    )
    return capakey_gateway
