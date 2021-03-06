# Generated by Django 2.1.5 on 2019-04-08 17:41

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
            field=models.PositiveIntegerField(blank=True, default=10000, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='waiting_list_limit',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
