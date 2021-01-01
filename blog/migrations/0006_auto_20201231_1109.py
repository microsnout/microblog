# Generated by Django 3.1.4 on 2020-12-31 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_post_blog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='status',
            field=models.CharField(choices=[('dormant', 'dormant'), ('offline', 'offline'), ('online', 'online')], default='offline', max_length=10),
        ),
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('draft', 'draft'), ('published', 'published')], default='draft', max_length=10),
        ),
    ]
