# Generated by Django 2.1.4 on 2018-12-28 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_image_display'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcounter',
            name='datestr',
            field=models.CharField(max_length=100),
        ),
    ]
