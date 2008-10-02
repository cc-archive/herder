# -*- coding: utf-8 -*-
import herder.tests
from minimock import Mock
from herder.tests import *
import herder.tests.functional.test_account
from herder.tests.functional.test_language import TestLanguageController
from herder.tests.functional.test_account import TestProfilePrefLangSpecificMail
from pylons import config
import git
import os

class TestMail(TestController):
    def test_no_git_change_for_most_edits(self):
        tlc = TestLanguageController()
        repo_dir = os.path.join(config.get('herder.po_dir'), 'cc_org')
        repo = git.Repository(repo_dir)
        
        # last commit on master
        starting_commit = repo.heads['refs/heads/master'].commit
        
        # edit a string...
        tlc.test_edit_string_as_bureau()

        # and assert that there was no update to the git repo
        ending_commit = repo.heads['refs/heads/master'].commit
        assert ending_commit.name == starting_commit.name

