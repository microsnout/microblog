# Generated by Django 3.1.4 on 2021-02-01 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20210131_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='signature',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='comment',
            name='annotation',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
