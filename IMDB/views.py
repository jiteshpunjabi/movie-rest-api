import logging
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import json, os
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from models import Movie, Genre
from apiAuth import has_perm, access_required

# Create your views here.

# setting up logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

@csrf_exempt
#@access_required
def get_movie(request, pk):
    """
    function to handle request for a particular movie
    GET => uesd to query
    POST w/o id, to insert and return inserted value
    POST w/ id, to update existing record
    :param request: incomming http request
    :param pk: primary key of the movie requested
    :return:
    """
    #check the incomming method
    try:
        if request.method == "GET":
            if pk != '':
                _movie = Movie.objects.get(pk=pk).json()
                response = HttpResponse(_movie, content_type="application/json")
                return response
            else:
                response = search_movie(request)
                return response
                raise Movie.MultipleObjectsReturned()
        elif request.method == 'POST':
            #check if user is authenticated to touch it
            #if pk='', insert, else overwrite
            if pk == '' and has_perm(request, 'IMDB.create_movie'):
                _m = Movie()
            elif pk != '' and has_perm(request, 'IMDB.change_movie'):
                _m = get_object_or_404(Movie, pk=pk)
            else:
                raise PermissionDenied()
            _m.add_using_json(request.body)
            _m.save()
            return HttpResponse(_m.json(), content_type="application/json", status=201)
        elif request.method == 'DELETE':
            if pk != '':
                if has_perm(request, 'delete_movie'):
                    _m = get_object_or_404(Movie, pk=pk)
                    _m.delete()
                    return HttpResponse('delete successful', content_type="application/json", status=200)
                else:
                    raise PermissionDenied()
            else:
                raise Movie.MultipleObjectsReturned()
        else:
            raise Movie.MultipleObjectsReturned()  #avoiding modification to the entire series
    except IntegrityError as ie:
        return HttpResponseBadRequest("{'status':400,'message':'Bad Request -- Integrity violation:" + ie.message + "'}",
                                        content_type="application/json")
    except KeyError as k:
        return HttpResponseBadRequest("{'status':400,'message':'Bad Request -- Key violation:" + k.message + "'}",
                                      content_type="application/json")
    except Movie.MultipleObjectsReturned as e:
        return HttpResponseNotFound(json.dumps({'status': 404, 'message': 'movie not found'}),
                                    content_type="application/json")
    except (Movie.DoesNotExist, Http404):
        return HttpResponseNotFound(json.dumps({'status': 404, 'message': 'movie not found'}),
                                    content_type="application/json")
    except PermissionDenied as p:
        return HttpResponseForbidden(json.dumps({'status': 403, 'message': 'Permission Denied{0:s}'.format(p.message)}),
                                     content_type="application/json")



@access_required
def search_movie(request):
    """genre=a+b+c&page_no=1&num_per_page=25
    """
    page_no=1
    field="name"
    query="django"
    try:
        if request.method == "GET":
            if request.GET.get("page_no"):
                page_no=int(request.GET["page_no"])
            if request.GET.get("query"):
                query=request.GET["query"]
            if request.GET.get("field"):
                field=request.GET["field"]
            return HttpResponse(Movie.objects.get_movies(20, page_no, query=query, field=field),
                        content_type="application/json")
        else:
            return HttpResponseNotAllowed(["GET"])
    except ValueError as e:
        return HttpResponseBadRequest("{'status':400,'message':'Bad Request -- Could not parse parameter" + e.message + "'}",
                                      content_type="application/json")
    except (Movie.DoesNotExist, Http404):
        return HttpResponseNotFound(json.dumps({'status': 404, 'message': 'movie not found'}),
                                    content_type="application/json")
#@access_required
def get_movie_page(request, page_no):
    return HttpResponse(Movie.objects.get_movies(20, page_no=int(page_no)),
                        content_type="application/json")





#utility function to batch load data from the sample file
def load_sample_data():
    file_path = os.path.abspath('/home/jiteshvp/Dev/ShopSense/InterviewExercise/data/imdb.json')
    with open(file_path, 'r') as f:
        _decoded_json = json.load(f)
        for _json_movie in _decoded_json:
            _movie = Movie(
                popularity=unicode_lower_strip(_json_movie['99popularity']),
                director=unicode_lower_strip(_json_movie['director']),
                movie_name=unicode_lower_strip(_json_movie['name'])
            )
            try:
                _movie.save()
                for _json_genre in _json_movie['genre']:
                    (_genre, _was_created) = Genre.objects.get_or_create(genre_label=unicode_lower_strip(_json_genre))
                    _movie.genre.add(_genre)
                _movie.save()
            except Exception as e:
                pass


def unicode_lower_strip(val):
    return unicode(val).strip().lower()