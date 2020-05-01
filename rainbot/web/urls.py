from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('post', views.PostDataView.as_view(), name='post'),
    path('data', views.GetDataView.as_view(), name='data'),
    path('counts', views.CountsView.as_view(), name='counts'),
    path('staticdata', views.StaticDataView.as_view(), name='staticdata')
]
