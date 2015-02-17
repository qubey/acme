from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from doc.models import Doctor, Patient, Vitals, PatientList
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

TABS = ['my_tab', 'all_tab', 'new_tab']

def normalize(text):
  return text.lower().strip()

def getDoctor(username):
  try:
    doc = Doctor.objects.get(username=username)
    return doc
  except ObjectDoesNotExist:
    pass

  # Create a new entry for the doctor if it doesn't exist already
  doc = Doctor(username=username)
  doc.save()
  return doc

def getPostParam(request, name):
  if request.method != "POST" or name not in request.POST:
    return None
  return request.POST[name]

def getUsername(request):
  username = None
  if 'uname' in request.COOKIES:
    username = request.COOKIES['uname']
  if request.method == 'POST' and 'uname' in request.POST:
    username = request.POST['uname']
  return username

def updateContext(context, selected_tab):
  for tab in TABS:
    if tab is selected_tab:
      context[tab] = 'tab-selected'
    else:
      context[tab] = 'tab'

def postProcessing(response, username):
  response.set_cookie('uname', username)
  return response

# Create your views here.
def index(request):
  username = getPostParam(request, 'uname')
  if username is not None and request.method == "POST":
    response = HttpResponseRedirect('/doc/my_patients')
    return postProcessing(response, username)

  # login page
  return render(request, 'doc/login.html')

def my_patients(request):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')

  doc = getDoctor(username)
  patient_list = PatientList.objects.filter(doctor=doc)
  patient_ids = [row.patient_id for row in patient_list]
  patients = Patient.objects.filter(id__in=patient_ids).order_by('last_name')

  context = {
    'username': username,
    'patients': patients
  }
  updateContext(context, 'my_tab')
  response = render(request, 'doc/doc_patients.html', context)
  return response

def all_patients(request):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')

  patients = Patient.objects.all().order_by('last_name')

  context = {
    'username':username,
    'patients': patients
  }
  updateContext(context, 'all_tab')
  response = render(request, 'doc/all_patients.html', context)
  return response

def patient_details(request, patient_id, join_care=None):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')

  patient = Patient.objects.get(id=patient_id)
  cur_doc = getDoctor(username)
  if join_care != None:
    if int(join_care) > 0:
      plist = PatientList(doctor=cur_doc, patient=patient)
      plist.save()
    else:
      PatientList.objects.filter(doctor=cur_doc, patient=patient).delete()
    

  doctors = PatientList.objects.filter(patient=patient)
  doctor_ids = [r.doctor_id for r in doctors]
  care_team = Doctor.objects.filter(id__in=doctor_ids).order_by('username')
  vitals = Vitals.objects.filter(patient=patient).order_by('-timestamp')[:50]

  grouped_vitals = { }
  for item in vitals:
    if item.name not in grouped_vitals:
      grouped_vitals[item.name] = {
        'value': item.value,
        'id': item.id,
      }

  join_text = "join"
  join_care = 1
  if cur_doc.id in doctor_ids:
    join_text = "leave"
    join_care = 0

  context = {
    'username': username,
    'patient': patient,
    'care_team': care_team,
    'vitals': grouped_vitals,
    'join_care': join_care,
    'join_care_text': join_text,
  }
  updateContext(context, 'details')
  response = render(request, 'doc/details.html', context)
  return response

def process_patient(request, username):
  first_name = getPostParam(request, 'first_name')
  last_name = getPostParam(request, 'last_name')

  fvalid = first_name != None and len(first_name) > 0
  lvalid = last_name != None and len(last_name) > 0
  if not fvalid or not lvalid:
    return None

  doctor = getDoctor(username)
  try:
    existing = Patient.objects.get(first_name=normalize(first_name), last_name=normalize(last_name))
    return existing.id
  except ObjectDoesNotExist:
    pass

  # Need to create a new one if the name doesn't exist
  patient = Patient(first_name=first_name, last_name=last_name)
  patient.save()

  plist = PatientList(doctor=doctor, patient=patient)
  plist.save()
  return patient.id

def new_patient(request):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')

  # If it's a valid form submission, go to the new patient details page
  if request.method == "POST":
    patient_id = process_patient(request, username)
    if patient_id is not None:
      return HttpResponseRedirect('/doc/patient_details/' + str(patient_id))

  context = {'username': username}
  updateContext(context, 'new_tab')
  response = render(request, 'doc/new_patient.html', context)
  return response

def add_vital(request, patient_id):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')

  patient = Patient.objects.get(id=patient_id)
  vital_name = getPostParam(request, 'vital_name')
  vital_value = getPostParam(request, 'vital_value')
  measure_time_str = getPostParam(request, 'measure_time')
  measure_time = None
  if measure_time_str != None:
    measure_time = datetime.strptime(
      getPostParam(request, 'measure_time'),
      '%Y-%m-%dT%H:%M'
    )
  if request.method == "POST" and vital_name != None and vital_value != None and measure_time != None:
    # Add vital and redirect
    new_vital = Vitals(patient=patient, name=vital_name, value=vital_value, timestamp=measure_time)
    new_vital.save()
    return HttpResponseRedirect('/doc/patient_details/' + str(patient_id))

  context = {
    'username': username,
    'patient': patient,
  }
  updateContext(context, 'add_vital')
  return render(request, 'doc/add_vital.html', context)

def discharge(request, patient_id):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')

  patient = Patient.objects.get(id=patient_id)
  if request.method == "POST":
    should_discharge = getPostParam(request, 'should_discharge')
    if should_discharge == "1":
      PatientList.objects.filter(patient=patient).delete()
      Vitals.objects.filter(patient=patient).delete()
      patient.delete()
      return HttpResponseRedirect('/doc/my_patients')

    # else
    return HttpResponseRedirect('/doc/patient_details/' + str(patient_id))


  context = {
    'username': username,
    'patient': patient,
  }
  updateContext(context, 'discharge')
  return render(request, 'doc/discharge.html', context)

def remove_vital(request, vital_id):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')
  
  vital = Vitals.objects.get(id=vital_id)
  patient_id = vital.patient_id
  vital_name = vital.name
  vital.delete()

  return HttpResponseRedirect('/doc/graph/' + str(patient_id) + '?table=1&vital_name=' + vital.name)

def graph(request, patient_id):
  username = getUsername(request)
  if username is None:
    return HttpResponseRedirect('/doc')

  if 'vital_name' not in request.GET:
    return HttpResponseRedirect('/doc/patient_details/' + str(patient_id))

  vital_name = request.GET['vital_name']

  table = 'false'
  if 'table' in request.GET:
    table = request.GET['table']

  patient = Patient.objects.get(id=patient_id)
  data = Vitals.objects.filter(
    patient=patient,
    name=vital_name
  ).order_by('-timestamp')[:20]
  tracked_vitals = Vitals.objects.filter(
    patient=patient
  ).order_by(
    'name'
  ).values_list('name', flat=True).distinct()

  show_error = False
  if len(data) < 2 and table != '1':
    table = '1'
    show_error = True
  
  context = {
    'username': username,
    'patient': patient,
    'vital_name': vital_name,
    'data': data,
    'tracked_vitals': list(tracked_vitals),
    'table': table,
    'show_error': show_error,
  }
  updateContext(context, 'graph')
  return render(request, 'doc/graph.html', context)
