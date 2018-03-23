# -*- coding: utf-8 -*
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--crab-integration",
        action="store_true",
        help="crab-integration: Run CRAB integration tests or not?"
    )
    parser.addoption(
        "--capakey-integration",
        action="store_true",
        help="capakey-integration: Run CAPAKEY integration tests or not?"
    )

@pytest.fixture(scope="module")
def capakey_rest_gateway():
    from crabpy.gateway.capakey import CapakeyRestGateway
    capakey_gateway = CapakeyRestGateway()
    return capakey_gateway
