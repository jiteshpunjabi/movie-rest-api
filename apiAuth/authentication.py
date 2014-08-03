__author__ = 'jiteshvp'
from django.conf import settings
import json
from django.http import HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse, NoReverseMatch
from models import Token
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

default_exemptions = ['auth_login', 'auth_register']

"""
    default timeout in minutes
"""
default_token_ttl = 5
token_ttl = getattr(settings,'token_ttl', default_token_ttl)
def get_exemptions():
    """
    :return: Set of exempted urls from either settings.py if configured else from the default_exemptions
    """
    exemptions = getattr(settings, 'API_AUTH_EXEMPT', default_exemptions)
    exempted_urls = []
    for exemption in exemptions:
        try:
            exempted_urls.append(reverse(exemption))
        except NoReverseMatch:
            logger.warning("reverse could not find view for exemption entry " +
                           exemption+" please check application settings")
    return exempted_urls

def get_api_key(request):
    api_key = None
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if auth_header is not None:
        tokens = auth_header.split(' ')
        if len(tokens) == 2 and tokens[0] == 'Token':
            api_key = tokens[1]
    return api_key



class Middleware(object):
    """
    This class puts the common logic to authenticate before letting any view process the request
    exemptions to these are names: auth_login, auth_logout and auth_register
    """

    def process_request(self, request):

        #if the requested path is in the list of exempted ones, return, else go check it out
        if request.path_info in get_exemptions():
            return
        allowed=False
        api_key = get_api_key(request)
        #check if a token exists
        if api_key is not None:
            token = Token.objects.check_hash(api_key)
            if token is not None:
                if (token.created+timezone.timedelta(minutes=token_ttl)) < timezone.now():
                    return HttpResponse(json.dumps({'status': 401, 'message': 'Session Timed Out'}), status=401,
                                             content_type="application/json")
            else:
                return HttpResponseForbidden(json.dumps({'status': 403, 'message': 'Authentication key invalid'}),
                                             content_type="application/json")
        else:
            return HttpResponseForbidden(json.dumps({'status': 403, 'message': 'Not allowed without API keys'}),
                                         content_type="application/json")
