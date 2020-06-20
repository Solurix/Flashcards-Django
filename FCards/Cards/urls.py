from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    # path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:set_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:set_id>/results/', views.results, name='results'),
    path('add_set/', views.add_folder, name='add_folder'),
    path('home/', views.home, name='home'),
    path('delete_set/<int:set_id>/', views.delete_folder, name='delete_folder')
]