# Generated by Django 2.1 on 2018-09-08 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20180908_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='display',
            field=models.BooleanField(null=True),
        ),
    ]
