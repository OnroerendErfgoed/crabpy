# -*- coding: utf-8 -*

import os
from six.moves import configparser

config = configparser.ConfigParser()

TEST_DIR = os.path.dirname(__file__)
config.read(os.path.join(TEST_DIR, 'test.ini'))


def run_crab_integration_tests():
    try:
        return config.getboolean('crab','run_integration_tests')
    except KeyError:  # pragma NO COVER
        return False


def run_capakey_integration_tests():
    try:
        return config.getboolean('capakey', 'run_integration_tests')
    except KeyError:  # pragma NO COVER
        return False
