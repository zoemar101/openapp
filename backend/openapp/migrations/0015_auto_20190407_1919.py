# Generated by Django 2.1.7 on 2019-04-07 11:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openapp', '0014_auto_20190407_1834'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='dateFrom',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='dateTo',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='date_modified',
        ),
        migrations.AddField(
            model_name='schedule',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='schedule',
            name='time',
            field=models.CharField(default=None, max_length=1000),
        ),
        migrations.AlterField(
            model_name='code',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='message',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='userattrib',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
    ]