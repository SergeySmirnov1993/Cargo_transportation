# Generated by Django 4.0.1 on 2022-01-22 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('load_place', models.CharField(max_length=100)),
                ('unload_place', models.CharField(max_length=100)),
                ('cargo', models.CharField(max_length=100)),
                ('weight', models.FloatField(default=0.0)),
                ('transport', models.CharField(max_length=100, null=True)),
                ('rates', models.FloatField(default=0.0)),
                ('tax', models.BooleanField(default=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_number', models.CharField(max_length=10)),
                ('brand', models.CharField(max_length=30)),
                ('model', models.CharField(max_length=30)),
                ('carrying', models.FloatField()),
            ],
        ),
    ]
