from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.projects_list, name='projects_list'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('donate/<int:project_id>/', views.donation_form, name='donation_form'),
    path('statistics/', views.statistics, name='statistics'),
]