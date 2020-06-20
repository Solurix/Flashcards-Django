from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:set_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:set_id>/results/', views.results, name='results'),

]