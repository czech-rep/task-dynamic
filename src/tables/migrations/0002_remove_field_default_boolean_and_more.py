# Generated by Django 5.0.4 on 2024-04-12 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='field',
            name='default_boolean',
        ),
        migrations.RemoveField(
            model_name='field',
            name='default_number',
        ),
        migrations.RemoveField(
            model_name='field',
            name='default_string',
        ),
        migrations.AddField(
            model_name='field',
            name='default',
            field=models.CharField(null=True),
        ),
    ]
