# Generated by Django 5.0.4 on 2024-04-12 13:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
                ('field_type', models.CharField(choices=[('string', 'String'), ('number', 'Number'), ('boolean', 'Boolean')])),
                ('default_number', models.IntegerField(null=True)),
                ('default_string', models.CharField(null=True)),
                ('default_boolean', models.BooleanField(null=True)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='tables.table')),
            ],
        ),
    ]
