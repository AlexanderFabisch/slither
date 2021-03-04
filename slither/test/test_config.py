import os
from slither.core.config import slither_ressource_filename
from nose.tools import assert_true


def test_resource_filename():
    filename = slither_ressource_filename("export.tcx.template")
    assert_true(os.path.exists(filename))
