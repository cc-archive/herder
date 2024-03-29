"""Pylons application test package

When the test runner finds and executes tests within this directory,
this file will be loaded to setup the test environment.

It registers the root directory of the project in sys.path and
pkg_resources, in case the project hasn't been installed with
setuptools. It also initializes the application via websetup (paster
setup-app) with the project's test.ini configuration file.
"""
import socket
import os
import sys
import time
import subprocess
import signal
import selenium
from unittest import TestCase

import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
from routes import url_for
import git
import os
from pylons import config

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

def socket_works(host, port, verbose = False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # for TCP IPv4
    try:
        sock.connect( (host, port) )
        return True
    except socket.error, sock_err:
        if verbose:
            print sock_err
        return False

# FIXME: Create a version of this that spin-loops until not listening
def spin_loop_until_listening_on_localhost_port(port,
                 max_time = 10, increment = 0.05):
    time_spent_on_this = 0
    has_worked = False
    while not has_worked:
        if time_spent_on_this > max_time:
            raise AssertionError, "Spent too long spin looping."
        time.sleep(increment)
        time_spent_on_this += increment
        has_worked = socket_works('localhost', port)
    return has_worked # should always be True

TEST_APP_PROCESS = None
TEST_APP_PORT = 5001
def start_app_process():
    assert not socket_works('localhost', TEST_APP_PORT)
    # LAME copy-pasta
    global TEST_APP_PROCESS
    # No need to setup-app because the test module will setup-app for us
    TEST_APP_PROCESS = subprocess.Popen(['./bin/paster', 'serve', '--reload', 'test.ini'])
    spin_loop_until_listening_on_localhost_port(TEST_APP_PORT, max_time = 60) # sometimes it takes a REALLY long time.

def stop_app_process():
    global TEST_APP_PROCESS
    os.kill(TEST_APP_PROCESS.pid, signal.SIGTERM)
    time.sleep(1) # spinloop until not listening, max timeout 1
    os.kill(TEST_APP_PROCESS.pid, signal.SIGKILL)
    time.sleep(1) # same spinloop as above
    assert TEST_APP_PROCESS.poll() is not None
    TEST_APP_PROCESS = None

SELENIUM_PROCESS = None
SELENIUM_BROWSER = None
SELENIUM_PORT = 4444
def start_selenium():
    global SELENIUM_PROCESS
    global SELENIUM_BROWSER
    SELENIUM_PROCESS = subprocess.Popen('./bin/selenium')
    assert not socket_works('localhost', SELENIUM_PORT)
    spin_loop_until_listening_on_localhost_port(SELENIUM_PORT)

    # Now, check that the process is still alive:
    assert SELENIUM_PROCESS.poll() is None
    # Then let's attach the BROWSER
    SELENIUM_BROWSER = selenium.selenium('localhost', SELENIUM_PORT,
                    '*firefox', 'http://localhost:5001')
    SELENIUM_BROWSER.start()
    return SELENIUM_BROWSER

def stop_selenium():
    global SELENIUM_PROCESS
    global SELENIUM_BROWSER
    os.kill(SELENIUM_PROCESS.pid, signal.SIGTERM)
    time.sleep(1)
    os.kill(SELENIUM_PROCESS.pid, signal.SIGKILL)
    time.sleep(1)
    assert SELENIUM_PROCESS.poll() is not None
    SELENIUM_PROCESS = None
    SELENIUM_BROWSER = None

# Now, trace things we know we're interested in seeing more about:
#url_for = trace(url_for)

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
        TestCase.__init__(self, *args, **kwargs)
        self._git_repo = None

    def runTest(self):
        pass

    def setUp(self):
        if config.get('herder.do_git_commits') == 'true':
            # Store info about the git Repo - 
            # particularly, the commit that master pointed to at the start
            assert self._git_repo is None
            self._git_repo = git.Repository(os.path.join(
                    config.get('herder.po_dir'), 'cc_org'))
            self._git_commit_at_start = self._git_repo.heads[
                'refs/heads/master'].commit
            assert ('example.com' not in
                    self._git_commit_at_start.author.email)

    def tearDown(self):
        if self._git_repo:
            # Make sure we chose a real commit to revert to
            assert ('example.com' 
                    not in self._git_commit_at_start.author.email)
            ref = git.Ref(self._git_repo, 'refs/heads/master')
            ref.update(self._git_commit_at_start)
            self._git_repo = None


    def login_as(self, username, password, should_fail = False):
        url = url_for(controller='account', action='login')
        response = self.app.get(url)
        response.forms[0]['username'] = username
        response.forms[0]['password'] = password

        if should_fail:
            try:
                response = response.forms[0].submit()
            except:
                # Great!  A failure.
                return True
            # That's a shame, no exception.
            assert False, "Login should have failed."
        else:
            response = response.forms[0].submit()
            
            # Now, follow the redirect
            response = response.follow()
            assert 'You were successfully logged in' in response
        return response

# Also, create a bureau user and store his password here.
from herder.tests.functional import test_account
controller = test_account.TestAuthControllerThree()
bureau_password = 'noeffingway_coffee_roflcopter'
bureau_username = 'oX2Pohxu'

__all__ = ['url_for', 'TestController', 'start_selenium', 'stop_selenium', 'start_app_process', 'stop_app_process', 'bureau_password', 'bureau_username']
