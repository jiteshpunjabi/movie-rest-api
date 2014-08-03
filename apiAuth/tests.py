from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from models import Token
from IMDB.models import Movie
import json, hmac,hashlib
from django.conf import settings
from django.http import HttpResponseForbidden

# Create your tests here.
class ViewsTest(TestCase):
    pass
class AuthenticationMiddlewareTest(TestCase):
    def test_add_movie_using_json_model(self):
        f = open('single_movie.json', 'r')
        m = Movie()
        m.add_using_json(f.read())
        m.save()
        self.assertEqual(Movie.objects.get(movie_name='three little pigs'),m)
    def test_token_generation(self):
        #setup
        self.test_add_movie_using_json_model()
        #create a login request and generate a token
        c = Client()
        #register a user
        response_register = c.post(reverse('auth_register'), {'username':'jitesh','password':'password','mailid':'jpunjabi@shopsense.co'})
        #try logging into that user
        response_login = c.post(reverse('auth_login'), {'username':'jitesh','password':'password'})
        #strip the token from the authentication header
        api_key_sent_to_user = json.loads(response_login.content)
        #hash the key using the same logic and verify if the user token was stored properly
        api_key_hash = hmac.new(str(api_key_sent_to_user['token']), getattr(settings,'SECRET_KEY','jiteshpunjabi'), hashlib.sha256).hexdigest().decode()
        print api_key_sent_to_user['token'], api_key_hash
        #check if there exists a token with the same api_key_hash
        abc = Token.objects.all().get()
        self.assertEqual(Token.objects.filter(token=api_key_hash).count(), 1)
        #send a get request for say '/movie/page/1'
        http_auth_header_content='Token '+api_key_sent_to_user['token']
        response = c.get('/movie/page/1', HTTP_AUTHORIZATION=http_auth_header_content)
        self.assertEqual(response.status_code, 200)
        #test a case without the header
        response = c.get('/movie/page/1')
        self.assertEqual(response.status_code, 403)
