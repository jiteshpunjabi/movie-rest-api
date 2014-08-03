from django.utils import unittest
from models import Movie, Genre
from django.test.client import Client
from django.core.urlresolvers import reverse

# Create your tests here.
class addMovieTest(unittest.TestCase):
    def test_add_movie_using_json_model(self):
        f = open('single_movie.json', 'r')
        m = Movie()
        m.add_using_json(f.read())
        m.save()
        self.assertEqual(Movie.objects.get(movie_name='three little pigs'),m)
    def _assert_add_label(self):
        pass
    #logout(request)
    #user = authenticate(username="jitesh", password="password")
    #login(request, user)
    #print User.objects.filter(username="jitesh").get().has_perm('IMDB.change_movie')

    def _assert_remove_label(self):
        pass
    def _assert_permissions_check(self):
        pass
    def _asert_pagination_check(self):
        pass
    def test_login_with_token(self):
        client = Client()
        #first try without registering, should return 403 permission denied
        response=client.post(reverse("auth_login"),data={'username':'jitesh','mail_id':'abc@abc.com','password':'password'})
        self.assertEqual(response.status_code,403)
        response = client.post(reverse("auth_register"),data={'username':'jitesh','mail_id':'abc@abc.com','password':'password'})
        self.assertEqual(response.status_code,200)
        response=client.post(reverse("auth_login"),data={'username':'jitesh','mail_id':'abc@abc.com','password':'password'})
        self.assertEqual(response.status_code,200)