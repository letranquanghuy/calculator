from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("calculate-result", views.calculate_result, name="calculate_result"),
    path("handle-percentage", views.handle_percentage, name="handle_percentage"),

    
]