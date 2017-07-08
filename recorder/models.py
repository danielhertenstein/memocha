from django.contrib.auth.models import User
from django.db import models


class Doctor(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)

class Person(models.Model):
    user = models.OneToOneField(User)
    # The doctors field may not be necessary? Are doctors users who will check
    # on Persons? Is there a way to tie the user to a model instance?
    doctors = models.ManyToManyField(Doctor)
    # Probably want to know what the person has been prescribed
    # (medication and dosage).

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)

class Medication(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Video(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    record_date = models.DateTimeField()
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    # Probably want to keep track of the dosage.
    # TODO: Hook this up correctly.
    upload = models.FileField()

    def __str__(self):
        return "{0} {1} {2} {3}".format(
            self.person.user.first_name,
            self.person.user.last_name,
            self.record_date,
            self.medication.name
        )
