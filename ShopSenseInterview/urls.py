from django.conf.urls import patterns, include, url
from apiAuth import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ShopSenseInterview.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^movie', include('IMDB.urls', namespace="movie")),
    url('login/',view=views.login_with_token,name="auth_login"),
    url('logout/',view=views.logout_with_token,name="auth_logout"),
    url('register/',view=views.do_register_user,name="auth_register"),
)
