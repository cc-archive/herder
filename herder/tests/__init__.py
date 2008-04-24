"""Pylons application test package

When the test runner finds and executes tests within this directory,
this file will be loaded to setup the test environment.

It registers the root directory of the project in sys.path and
pkg_resources, in case the project hasn't been installed with
setuptools. It also initializes the application via websetup (paster
setup-app) with the project's test.ini configuration file.
"""
import os
import sys
from unittest import TestCase

import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
from routes import url_for

__all__ = ['url_for', 'TestController']

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)
pkg_resources.working_set.add_entry(conf_dir)
pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

test_file = os.path.join(conf_dir, 'test.ini')
# remove the old database from last test run
DB_FILENAME = os.path.join(conf_dir, 'herder_test.db') # Pull from conf?
if os.path.exists(DB_FILENAME):
    os.unlink(DB_FILENAME)

cmd = paste.script.appinstall.SetupCommand('setup-app')
cmd.run([test_file])

## FIXME: Use a standard @trace decorator
def trace(fn):
    def traced(*argv, **kwargs):
        print fn.__name__, '(', argv,
        if kwargs:
            print '+', kwargs,
        print ') =>',
        ret = fn(*argv, **kwargs)
        print ret
        return ret
    return traced

# Now, trace things we know we're interested in seeing more about:
url_for = trace(url_for)

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
        TestCase.__init__(self, *args, **kwargs)
