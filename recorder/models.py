from django.db import models


class Doctor(models.Model):
    # TODO: Probably move these details and the ones in Person to a metaclass
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    # The doctors field may not be necessary? Are doctors users who will check
    # on Persons? Is there a way to tie the user to a model instance?
    doctors = models.ManyToManyField(Doctor)
    # Probably want to know what the person has been prescribed
    # (medication and dosage).

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

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
            self.person.first_name,
            self.person.last_name,
            self.record_date,
            self.medication.name
        )
