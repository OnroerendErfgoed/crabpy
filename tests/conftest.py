import json
import os
import re

import pytest
import responses
from unittest.mock import Mock

from crabpy.gateway.crab import CrabGateway

CAPAKEY_URL = 'https://geoservices.informatievlaanderen.be/capakey/api/v2'


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


def load_json(filename):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, 'dummy_responses', filename)) as file:
        return json.load(file)


@pytest.fixture(scope="module")
def capakey_rest_gateway():
    from crabpy.gateway.capakey import CapakeyRestGateway
    capakey_gateway = CapakeyRestGateway()
    return capakey_gateway


@pytest.fixture(scope='function')
def crab_service(crab_client_mock):
    return crab_client_mock.service


@pytest.fixture(scope='function')
def crab_client_mock():
    crab_client = Mock()
    crab_client.service.ListBewerkingen.return_value = Mock(
        CodeItem=[Mock(Code=1)]
    )
    crab_client.service.ListOrganisaties.return_value = Mock(
        CodeItem=[Mock(Code=1)]
    )
    return crab_client


@pytest.fixture(scope='function')
def crab_gateway(crab_client_mock):
    return CrabGateway(crab_client_mock)


@pytest.fixture(scope='function')
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope='function')
def municipalities_response(mocked_responses):
    mocked_responses.add(
        method='GET',
        url=f'{CAPAKEY_URL}/municipality?',
        json=load_json('municipalities.json')
    )


@pytest.fixture(scope='function')
def municipality_response(mocked_responses):
    url = re.compile(
        fr'{CAPAKEY_URL}/municipality/\d+\?'
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('municipality.json')
    )


@pytest.fixture(scope='function')
def municipality_department_response(mocked_responses):
    url = re.compile(
        r'{capakey}/municipality/\d+/department\?'
        .format(capakey=CAPAKEY_URL)
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('municipality_department.json')
    )


@pytest.fixture(scope='function')
def department_response(mocked_responses):
    url = re.compile(
        fr'{CAPAKEY_URL}/department/\d+\?'
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('department.json')
    )


@pytest.fixture(scope='function')
def department_sections_response(mocked_responses):
    url = re.compile(
        r'{capakey}/municipality/\d+/department/\d+/section$'
        .format(capakey=CAPAKEY_URL)
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('department_sections.json')
    )


@pytest.fixture(scope='function')
def department_section_response(mocked_responses):
    url = re.compile(
        r'{capakey}/municipality/\d+/department/\d+/section/[^/]+\?'
        .format(capakey=CAPAKEY_URL)
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('department_section.json')
    )


@pytest.fixture(scope='function')
def department_section_parcels_response(mocked_responses):
    url = re.compile(
        r'{capakey}/municipality/\d+/department/\d+/section/[^/]+/parcel\?'
        .format(capakey=CAPAKEY_URL)
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('department_section_parcels.json')
    )


@pytest.fixture(scope='function')
def department_section_parcel_response(mocked_responses):
    url = re.compile(
        r'{capakey}/municipality/\d+/department/\d+/section/[^/]+/parcel/'
        r'\d+/[^/]+\?'
        .format(capakey=CAPAKEY_URL)
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('department_section_parcel.json')
    )


@pytest.fixture(scope='function')
def parcel_response(mocked_responses):
    url = re.compile(
        r'{capakey}/parcel/[^/]+/[^/]+\?'
        .format(capakey=CAPAKEY_URL)
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('parcel.json')
    )


@pytest.fixture(scope='function')
def parcels_response(mocked_responses):
    url = re.compile(
        r'{capakey}/parcel\?'
        .format(capakey=CAPAKEY_URL)
    )
    mocked_responses.add(
        method='GET',
        url=url,
        json=load_json('parcel.json')
    )
