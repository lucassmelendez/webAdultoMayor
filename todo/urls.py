from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('' , views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('talleres/', views.talleres, name='talleres'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('toggle-inscripcion/<int:taller_id>/', views.toggle_inscripcion, name='toggle-inscripcion'),
    path('perfil/editar/', views.update_profile, name='update_profile'),
]