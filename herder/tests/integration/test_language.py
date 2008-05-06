from herder.tests import *
import herder.tests

class TestLanguageController(TestController):
    def test_the_works(self):
        # First, pretend to be the admin user.
        herder.tests.start_selenium()
        herder.tests.SELENIUM_BROWSER.open('http://localhost:5001/')
        
        # Add a language called fake
        # Note that all the strings are untranslated
        # (that is, all == untranslated)
        # Translate one string, and check it goes away from untranslated
        # Check that it gets stored in a way that we can pull it out?
        herder.tests.stop_selenium()
        pass
