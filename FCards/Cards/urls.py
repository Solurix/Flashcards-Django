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
    path('delete_set/<int:set_id>/', views.delete_folder, name='delete_folder'),
    path('edit_set/<int:set_id>/', views.edit_folder, name='edit_folder'),
    path('add_multicard/<int:set_id>/', views.add_multicard, name='add_multicard'),
    path('add_many/<int:set_id>/', views.add_many, name='add_many'),
    path('edit_multicards/<int:set_id>/', views.edit_multicards, name='edit_multicards'),
]