from django.core import paginator
from django.db import models, IntegrityError, connection
from django.contrib.auth.models import User
import logging
import json
import decimal
import os, binascii
from django.core.paginator import Paginator
from django.http import Http404
# Create your models here.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Genre(models.Model):
    genre_label = models.CharField(name="genre_label",
                                   verbose_name="Genre Label",
                                   max_length=50, unique=True)
    class Meta:
        pass


class MovieManager(models.Manager):
    def get_movies(self, no_per_page=20, page_no=1,field="name", query=""):
        query_set=[]
        if field == "genre":
            _genre = query.split("+") #cleanse the genre set given
            query_set = self.get_queryset().filter(genre__genre_label__in=_genre).prefetch_related() #filter and obtain the queryset
        elif field == "name" or field == "director":
            cursor = connection.cursor()
            cursor.execute("SELECT id from IMDB_movie_search_index WHERE MATCH(director,movie_name) AGAINST(%s)", [query])
            r = [x for (x,) in cursor.fetchall()]
            if len(r) > 0:
                query_set = self.get_queryset().filter(id__in=r).prefetch_related()
            else:
            #run a raw query, see if you fetch anything...if yes great...if not fall back to advanced
                query_set = self.get_queryset()
                words = unicode_lower_strip(query).split("+")
                if field == "name":
                    for word in words:
                        query_set = query_set.filter(movie_name__contains=word)
                elif field == "director":
                    for word in words:
                        query_set = query_set.filter(director__contains=word)
        else:
            query_set = self.get_queryset().prefetch_related('genre') #a normal page request

        #if there are no results, raise a 404 not found
        if len(query_set) == 0:
            raise Http404()

        #set up paginator and respond
        p = Paginator(query_set, no_per_page)
        if page_no > p.num_pages:
            page_no = p.num_pages
        elif page_no < 1:
            page_no = 1
        _data = self.__dict_list__(p.page(page_no))

        #adding the metadata
        _output = {'metadata':{'model':'movie', 'page':page_no, 'total_pages':p.num_pages},'data':_data}
        if query != "":
            _output["search"] = {'field': field,'query': query}

        # and at last, we have our result!
        return json.dumps(_output, default=default_decimal_override, indent=4)



    def __dict_list__(self, movie_query_set):
        _data = []
        for x in movie_query_set:
            if isinstance(x, Movie):
                _data.append(x.__asdict__())
                pass
            else:
                raise TypeError()
        return _data
        #create dictionary, add to list, parse to json using the default_decimal_override


class Movie(models.Model):
    objects=MovieManager()
    popularity = models.DecimalField(verbose_name="Popularity",
                                     name="popularity",
                                     max_digits=4,
                                     decimal_places=2,
                                     )
    director = models.CharField(name="director",
                                verbose_name="Director",
                                max_length="400",
                                )
    genre = models.ManyToManyField(to=Genre)
    movie_name = models.CharField(name="movie_name",
                                  verbose_name="Movie Name",
                                  max_length=500,
                                  )
    class Meta:
        unique_together = ('director','movie_name')
        ordering = ['-popularity']
    def imdb_score(self):
        return self.popularity / 10.0

    def _parse_dict_to_movie(self, _json_dict):
        self.director = unicode_lower_strip(_json_dict['director'])
        self.movie_name = unicode_lower_strip(_json_dict['name'])
        self.popularity = _json_dict['popularity']
        self.save()
        _set_new_genre = set()
        _set_old_genre = set(self.genre.all())
        for _json_genre in _json_dict['genre']:
            (_genre, _was_created) = Genre.objects.get_or_create(genre_label=unicode_lower_strip(_json_genre))
            _set_new_genre.add(_genre)
            self.genre.add(_genre)
        #delete the additional genres
        for _genre in _set_old_genre-_set_new_genre:
            self.genre.remove(_genre)
        self.save()

    def add_using_json(self, json_data):
        """
        Note that the method can possibly raise KeyError, IntegrityError. Calling method should handle as appropriate
        :param json_data:
        :return:
        """
        if json_data is not None:
            #try parsing json data
            try:
                _dict = json.loads(json_data,)
                self._parse_dict_to_movie(_dict)
            except KeyError as k:
                logger.exception(k.message)
                raise k
            except IntegrityError as i:
                logger.exception(i.message)
                raise i
        else:
            logger.exception("None passed to add_using json")
            raise AttributeError()

    def __asdict__(self):
        _dict = {
            'pk' :self.pk,
            'name': self.movie_name.title(),
            'popularity': self.popularity,
            'director': self.director.title(),
            'genre': [_genre.genre_label for _genre in self.genre.all()]
        }
        return _dict

    def json(self):
        return json.dumps(self.__asdict__(), default=default_decimal_override)





#utility functions
def unicode_lower_strip(val):
    return unicode(val).strip().lower()

def default_decimal_override(x):
    if isinstance(x, decimal.Decimal):
        return float(x)