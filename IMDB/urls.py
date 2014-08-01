__author__ = 'jiteshvp'
from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                        url('^/page/(?P<page_no>\d+)',view=views.get_movie_page,name="movie_page"),
                        url('^/(?P<pk>\d*)$',view=views.get_movie,name="get_movie"),
                        url('^/search',view=views.search_movie,name="search_movies"),

                    )