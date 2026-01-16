from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('complaint/new/', views.file_complaint, name='file_complaint'),
    path('complaints/', views.my_complaints, name='my_complaints'),
    path('complaint/pdf/<int:complaint_id>/', views.complaint_pdf, name='complaint_pdf'),
]
