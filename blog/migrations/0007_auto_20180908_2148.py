# Generated by Django 2.1 on 2018-09-08 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20180908_2143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='author',
            new_name='contributor_author',
        ),
    ]
