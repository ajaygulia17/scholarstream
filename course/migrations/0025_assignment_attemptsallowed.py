# Generated by Django 4.2.1 on 2023-07-14 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0024_assignmentprogress_created_at_othergrade_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='attemptsAllowed',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
