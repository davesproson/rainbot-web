from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('post', views.PostDataView.as_view(), name='post'),
    path('data', views.GetDataView.as_view(), name='data')
]
