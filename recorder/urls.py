from django.conf.urls import url

from . import views


app_name = 'recorder'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^patient/$', views.patient_dashboard, name='patient_dashboard'),
    url(r'^patient/record', views.record_video, name='record_video'),
    url(r'^doctor/$', views.doctor_dashboard, name='doctor_dashboard'),
    url(r'^doctor/(?P<patient_id>[0-9]+)/$', views.patient_details, name='patient_details'),
    url(r'^new_patient/', views.patient_creation, name='patient_creation'),
    url(r'^new_doctor/', views.doctor_creation, name='doctor_creation'),
    url(r'^add_patient/', views.add_patient, name='add_patient')
]