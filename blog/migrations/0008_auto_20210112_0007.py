# Generated by Django 3.1.4 on 2021-01-12 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20210108_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='one_comment',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='blog',
            name='created',
            field=models.DateField(auto_now_add=True),
        ),
    ]
