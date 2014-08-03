from django.http import HttpResponseForbidden
from models import Token
import json

"""

use is deprecated.....include the middleware instead.

"""
def has_perm(request, permission):
    api_key = get_api_key(request)
    if api_key is not None:
        token = Token.objects.get(token=api_key)
        user = token.user
        return user.has_perm(permission)
    return False

def get_api_key(request):
    api_key = None
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if auth_header is not None:
        tokens = auth_header.split(' ')
        if len(tokens) == 2 and tokens[0] == 'Token':
            api_key = tokens[1]
    return api_key

#todo - make following available as a decorator
def access_required(func):
    def inner_decorator(request, *args, **kwargs):
        allowed=False
        api_key = get_api_key(request)
        #check if a token exists
        if api_key is not None:
            token = Token.objects.get(token=api_key)
            if token is not None:
                allowed = True
        if allowed:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(json.dumps({'status': 403, 'message': 'Access Denied'}),
                                                        content_type="application/json")
    return inner_decorator