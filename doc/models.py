from django.db import models

class Doctor(models.Model):
  username = models.CharField(max_length=200)

  def __unicode__(self):
    return self.username

class Patient(models.Model):
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)

  def __unicode__(self):
    return self.first_name + " " + self.last_name

class Vitals(models.Model):
  patient = models.ForeignKey(Patient)
  name = models.CharField(max_length=50)
  value = models.FloatField(default=0)
  timestamp = models.DateTimeField()

class PatientList(models.Model):
  doctor = models.ForeignKey(Doctor)
  patient = models.ForeignKey(Patient)
