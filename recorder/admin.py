from django.contrib import admin
from .models import Doctor, Patient, Prescription


admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Prescription)