from django.urls import path

from . import views, learn

urlpatterns = [
    path('add_set/', views.add_folder, name='add_folder'),
    path('home/', views.home, name='home'),
    path('delete_set/<int:set_id>/', views.delete_folder, name='delete_folder'),
    path('edit_set/<int:set_id>/', views.edit_folder, name='edit_folder'),
    path('copy_set/<int:set_id>/', views.copy_folder, name='copy_folder'),
    path('view_set/<int:set_id>/', views.view_folder, name='view_folder'),
    path('view_set_public/<int:set_id>/', views.view_folder_public, name='view_folder_public'),
    path('add_multicard/<int:set_id>/', views.add_multicard, name='add_multicard'),
    path('add_many/<int:set_id>/', views.add_many, name='add_many'),
    path('edit_multicards/<int:set_id>/', views.edit_multicards, name='edit_multicards'),
    path('delete_multicards/<int:set_id>/<int:m_card_id>/', views.delete_multicards, name='delete_multicards'),
    path('edit_multicards_save/<int:set_id>/<int:m_card_id>/', views.edit_multicards_save, name='edit_multicards_save'),
    path('edit_all_multicards/<int:set_id>/', views.edit_all_multicards, name='edit_all_multicards'),
    path('learn/learn/<int:set_id>/', learn.learn, name='learn'),
    path('learn/write/<int:set_id>/', learn.write, name='write'),
    path('learn/flashcards/<int:set_id>/', learn.flashcards, name='flashcards'),
    path('reset_progress/<int:set_id>/', views.reset_progress, name='reset_progress'),
    path('make_public/<int:set_id>/', views.make_public, name='make_public'),
    path('refresh_update/<int:set_id>/', views.refresh_update, name='refresh_update'),
    path('repair_translations/<int:set_id>/', views.repair_translations, name='repair_translations'),
    path('public_sets/', views.public_sets, name='public_sets'),
]
