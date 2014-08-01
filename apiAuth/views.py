from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from models import Token
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponseNotAllowed
from django.core.exceptions import PermissionDenied
import json
from django.db import IntegrityError

@csrf_exempt
def do_register_user(request):
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)
    mail_id = request.POST.get('mailid',None)
    try:
        if username is not None and password is not None and mail_id is not None:
            User.objects.create_user(username,email=mail_id, password=password)
            return login_with_token(request)
        else:
            raise AttributeError()
    except AttributeError as k:
        return HttpResponseBadRequest("{'status':400,'message':'Bad Request" + k.message + "'}",
                                      content_type="application/json")
@csrf_exempt
def login_with_token(request):
    """
    this will be a get request with the username and password. Response will be a json response where we will pass the username and auth token
    :param request:
    :return:
    """
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    try:

        if username is not None and password is not None:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    role = "user"
                    if user.is_staff:
                        role = 'admin'
                    _dict = {'username': username, 'token': token.__unicode__(), 'role':role }
                    return HttpResponse(json.dumps(_dict), content_type="application/json")
                else:
                    raise PermissionDenied()
            else:
                raise PermissionDenied()
        else:
            raise AttributeError()
    except AttributeError as k:
        return HttpResponseBadRequest("{'status':400,'message':'Bad Request" + k.message + "'}",
                                      content_type="application/json")
    except PermissionDenied as p:
        return HttpResponseForbidden(json.dumps({'status': 403, 'message': 'Check username and password{0:s}'.format(p.message)}),
                                    content_type="application/json")
    except IntegrityError as ie:
        return HttpResponseBadRequest(json.dumps({'status':400,'message':'Bad Request -- User already exists:' + ie.message}),
                                    content_type="application/json")
@csrf_exempt
def logout_with_token(request):
    return HttpResponse('')