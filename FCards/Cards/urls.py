from django.urls import path

from . import views, play

urlpatterns = [
    path('add_set/', views.add_folder, name='add_folder'),
    path('home/', views.home, name='home'),
    path('delete_set/<int:set_id>/', views.delete_folder, name='delete_folder'),
    path('edit_set/<int:set_id>/', views.edit_folder, name='edit_folder'),
    path('view_set/<int:set_id>/', views.view_folder, name='view_folder'),
    path('add_multicard/<int:set_id>/', views.add_multicard, name='add_multicard'),
    path('add_many/<int:set_id>/', views.add_many, name='add_many'),
    path('edit_multicards/<int:set_id>/', views.edit_multicards, name='edit_multicards'),
    path('delete_multicards/<int:set_id>/<int:m_card_id>/', views.delete_multicards, name='delete_multicards'),
    path('edit_multicards_save/<int:set_id>/<int:m_card_id>/', views.edit_multicards_save, name='edit_multicards_save'),
    path('edit_all_multicards/<int:set_id>/', views.edit_all_multicards, name='edit_all_multicards'),
    path('play/<int:set_id>/', play.play, name='play'),
]