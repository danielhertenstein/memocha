from django.conf.urls import url

from . import views


app_name = 'recorder'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^patient/', views.patient_dashboard, name='patient_dashboard'),
    url(r'^doctor/', views.doctor_dashboard, name='doctor_dashboard'),
]