# Generated by Django 5.0.4 on 2024-04-11 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0008_alter_field_field_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='table',
            options={},
        ),
        migrations.RemoveField(
            model_name='table',
            name='name',
        ),
    ]