import herder.tests
from herder.tests import *
import herder.model.role
import herder.model.meta

class TestRoles(TestController):

    def test_roles_exist(self):
        '''Ensure administer and translate roles exist'''
        admin_role = herder.model.meta.Session.query(herder.model.role.Role).get_by(
            role_name='administer')
        assert admin_role is not None
        translate_role = herder.model.meta.Session.query(herder.model.role.Role).get_by(
            role_name='translate')
        assert translate_role is not None

