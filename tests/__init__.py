import contextlib
import os
from six.moves import configparser

from crabpy.gateway import adressenregister

config = configparser.ConfigParser()

TEST_DIR = os.path.dirname(__file__)
config.read(os.path.join(TEST_DIR, "test.ini"))
adressenregister.setup_cache(
    {"long.backend": "dogpile.cache.null", "short.backend": "dogpile.cache.null"}
)


def run_crab_integration_tests():
    try:
        return config.getboolean("crab", "run_integration_tests")
    except KeyError:  # pragma NO COVER
        return False


def run_capakey_integration_tests():
    try:
        return config.getboolean("capakey", "run_integration_tests")
    except KeyError:  # pragma NO COVER
        return False


@contextlib.contextmanager
def memory_cache():
    try:
        adressenregister.setup_cache(
            {
                "long.backend": "dogpile.cache.memory",
                "short.backend": "dogpile.cache.memory"
            }
        )
        yield
    finally:
        adressenregister.setup_cache(
            {
                "long.backend": "dogpile.cache.null",
                "short.backend": "dogpile.cache.null"
            }
        )
