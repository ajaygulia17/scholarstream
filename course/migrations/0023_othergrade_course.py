# Generated by Django 4.2.1 on 2023-07-02 06:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0022_othergrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='othergrade',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.course'),
        ),
    ]
