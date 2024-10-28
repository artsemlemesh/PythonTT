from django.urls import path
from . import views

urlpatterns = [
    path('', views.email_list_view, name='email_list'),
    path('import/<int:account_id>/', views.start_email_import, name='start_email_import'),
]