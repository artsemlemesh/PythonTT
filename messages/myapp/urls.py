from django.urls import path
from . import views

urlpatterns = [
    path('emails/', views.email_list_view, name='email_list'),
    path('emails/import/<int:account_id>/', views.start_email_import, name='start_email_import'),
]