from django.db import models


class Doctor(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    # The doctors field may not be necessary? Are doctors users who will check
    # on Persons? Is there a way to tie the user to a model instance?
    doctors = models.ManyToManyField(Doctor)
    # Probably want to know what the person has been prescribed
    # (medication and dosage).

class Medication(models.Model):
    name = models.CharField(max_length=100)

class Video(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    record_date = models.DateTimeField()
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    # Probably want to keep track of the dosage.
    # Need a field for the actual video file.
