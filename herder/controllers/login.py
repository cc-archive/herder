from herder.lib.base import *
import herder.model.user
import sha

class LoginController(BaseController):
    requires_auth = ['required']

    def required(self):
        redirect_to('/')

    def logout(self):
        '''Log the user out and display a confirmation message'''
        if 'user' in session:
            del session['user']
            session.save()
        return render('/account/logout.html')
        
