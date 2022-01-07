from django.urls import path
from .views import *

urlpatterns = [
    path('<slug:id>', HomePage.as_view(), name='view2'),
    path('', HomePage.as_view(), name='view'),

]