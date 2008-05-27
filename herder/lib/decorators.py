from decorator import decorator
from pylons import c, cache, config, g, request, response, session

@decorator
def with_user_info(fn, *args, **kwargs):
    """Inject information about the logged in user and global roles 
    into the context."""

    # inject some stuff into the context
    c.user = session.get('user', None)

    return fn(*args, **kwargs)

