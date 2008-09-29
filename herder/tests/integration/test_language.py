from herder.tests import *
import time

class TestLanguageController(TestController):
    def disabled_t3st_for_YUI_space_bug(self):
        start_app_process()
        sel = start_selenium()
        # First, pretend to be the bureau user.
        sel.open('http://localhost:5001' + 
                 url_for(controller='account',
                             action='login'))
        sel.type('username', bureau_username)
        sel.type('password', bureau_password)
        sel.click('authform')
        sel.wait_for_page_to_load(3000)

        # Then go on
        sel.click("link=Translation Domains")
        sel.wait_for_page_to_load(3000)
        
        sel.click("link=cc_org")
        sel.wait_for_page_to_load(3000)
        sel.click("link=en_US")
        sel.wait_for_page_to_load(3000)

        sel.click("link=all")
        sel.wait_for_page_to_load(30000)

        # Wait for country.us + table
        for i in range(60):
            try:
                if sel.is_text_present("country.us"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")

        # Make sure the box is in the place we think
        self.failUnless("^exact:<a href=\"/domain/cc_org[\\s\\S]domain=cc_org\">cc_org</a>: <a href=\"/domain/cc_org/language/en_US/view\">en_US</a>: All Strings$")
        # change it!
        sel.click("//td[@id='yui-dt0-bdrow0-cell2']/div")

        # Wait for OK button
        for i in range(60):
            try:
                if sel.is_text_present("OK"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")

        sel.type("//div[@id='yui-dt0-celleditor']/textarea", "Plus+States")
        sel.click("//div[@id='yui-dt0-celleditor']/div[1]/button[1]")

        for i in range(60 * 10):
            try:
                if sel.is_text_present("Translation updated"): break
            except: pass
            time.sleep(0.1)
        else: self.fail("time outt")

        assert (sel.is_text_present('Plus+States') or
                sel.is_text_present('Plus States')) # this always fails,
        # even though we really do click OK.  weird.

        # check what it got set to
        
        # Add a language called fake
        # Note that all the strings are untranslated
        # (that is, all == untranslated)
        # Translate one string, and check it goes away from untranslated
        # Check that it gets stored in a way that we can pull it out?
        stop_selenium()
        stop_app_process()
