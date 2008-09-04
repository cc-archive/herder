import herder.tests
from herder.tests import *
import herder.model.user
import herder.model.role
import herder.model.meta
import herder.model.authorization
import herder.tests.functional.test_account

class TestRoles(TestController):

    def test_roles_exist(self):
        '''Ensure bureaucrat and translator roles exist'''
        bureau_role = herder.model.meta.Session.query(herder.model.role.Role).filter_by(
            role_name='bureaucrat').first()
        assert bureau_role is not None
        translator_role = herder.model.meta.Session.query(herder.model.role.Role).filter_by(
            role_name='translator').first()
        assert translator_role is not None

class TestAuthorization(TestController):

    def test_can_grant_star_to_someone(self):
        '''Try create a new user and make him a global bureaucrat'''
        user_name = herder.model.user.random_alphanum()
        password = herder.model.user.random_alphanum()
        herder.tests.functional.test_account.do_register(self.app, user_name=user_name,
            password=password, human_name='Secret Backdoor Bureaucrat')

        # Find the right user object
        user_obj = herder.model.meta.Session.query(herder.model.user.User).filter_by(
            user_name=user_name).first()

        # Create the all bureaucrat object
        all_bureaucrat = herder.model.authorization.Authorization()
        all_bureaucrat.user_id = user_obj.user_id
        all_bureaucrat.lang_id = '*'
        all_bureaucrat.domain_id = '*'
        all_bureaucrat.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(
            role_name='bureaucrat').first().role_id
        herder.model.meta.Session.save(all_bureaucrat)

        # Create the all translator object
        all_translator = herder.model.authorization.Authorization()
        all_translator.user_id = user_obj.user_id
        all_translator.lang_id = '*'
        all_translator.domain_id = '*'
        all_translator.role_id = herder.model.meta.Session.query(herder.model.role.Role).filter_by(
            role_name='translator').first().role_id
        herder.model.meta.Session.save(all_translator)

        # Sync
        herder.model.meta.Session.commit()

        # Grab it out again
        assert len(herder.model.meta.Session.query(herder.model.authorization.Authorization).filter_by(
            user_id=user_obj.user_id).all()) == 2
