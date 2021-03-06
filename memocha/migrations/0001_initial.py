# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-18 16:53
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField()),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memocha.Doctor')),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medication', models.CharField(max_length=100)),
                ('dosage', models.CharField(max_length=100)),
                ('dosage_times', django.contrib.postgres.fields.ArrayField(base_field=models.TimeField(), size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_date', models.DateTimeField()),
                ('upload', models.FileField(upload_to='videos/')),
                ('approved', models.NullBooleanField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memocha.Patient')),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memocha.Prescription')),
            ],
        ),
        migrations.AddField(
            model_name='patient',
            name='prescriptions',
            field=models.ManyToManyField(blank=True, to='memocha.Prescription'),
        ),
        migrations.AddField(
            model_name='patient',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
