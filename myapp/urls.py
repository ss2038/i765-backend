from django.urls import path
from .views import retrieveDetails, createUsername, fillDetail, fill_pdf

urlpatterns = [
    path('api/user/create/', createUsername, name='create-username'),
    path('api/user/fill-detail/', fillDetail, name='fill-detail'),
    path('api/user/<str:username>/', retrieveDetails, name='retrieve-details'),
    path('pdf/fill/<str:username>/', fill_pdf, name='fill-pdf'),
]
