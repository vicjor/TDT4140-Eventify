# Generated by Django 2.1.5 on 2019-02-21 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_auto_20190318_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='attendance_limit',
            field=models.IntegerField(default=10000, null=True),
        ),
    ]
