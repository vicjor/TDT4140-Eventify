# Generated by Django 2.1.5 on 2019-04-07 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_merge_20190407_1418'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['start_date']},
        ),
        migrations.AlterField(
            model_name='post',
            name='attendance_limit',
            field=models.PositiveIntegerField(blank=True, default=10000, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
