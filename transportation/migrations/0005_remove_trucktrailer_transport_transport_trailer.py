# Generated by Django 4.0.1 on 2022-03-08 10:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0004_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trucktrailer',
            name='transport',
        ),
        migrations.AddField(
            model_name='transport',
            name='trailer',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transport', to='transportation.trucktrailer'),
        ),
    ]