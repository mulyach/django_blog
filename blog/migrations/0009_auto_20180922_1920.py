# Generated by Django 2.1 on 2018-09-22 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ['caption']},
        ),
        migrations.RenameField(
            model_name='image',
            old_name='name',
            new_name='caption',
        ),
        migrations.AlterField(
            model_name='image',
            name='img_file',
            field=models.ImageField(null=True, upload_to='', verbose_name=''),
        ),
    ]
