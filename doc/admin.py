from django.contrib import admin
from doc.models import Doctor
from doc.models import Patient
from doc.models import Vitals
from doc.models import PatientList

# Register your models here.
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Vitals)
admin.site.register(PatientList)
