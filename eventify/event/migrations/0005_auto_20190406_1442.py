# Generated by Django 2.1.5 on 2019-04-06 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_merge_20190318_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='attendance_limit',
            field=models.IntegerField(blank=True, default=10000, null=True),
        ),
    ]
