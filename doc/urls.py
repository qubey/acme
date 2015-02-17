from django.conf.urls import patterns, url
from doc import views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),
  url(r'^my_patients$', views.my_patients, name='doc_patients'),
  url(r'^all_patients$', views.all_patients, name='all_patients'),
  url(
    r'^patient_details/(?P<patient_id>\d+)$',
    views.patient_details,
    name='patient_details'
  ),
  url(
    r'^patient_details/(?P<patient_id>\d+)/(?P<join_care>\d+)$',
    views.patient_details,
    name='patient_details_join'
  ),
  url(r'^new_patient', views.new_patient, name='new_patient'),
  url(r'^add_vital/(?P<patient_id>\d+)$', views.add_vital, name="new_vital"),
  url(r'^discharge/(?P<patient_id>\d+)$', views.discharge, name='discharge'),
  url(r'^remove_vital/(?P<vital_id>\d+)$', views.remove_vital, name='remove_vital'),
  url(r'^graph/(?P<patient_id>\d+)$', views.graph, name='graph'),
)
