# Generated by Django 3.2.16 on 2024-06-08 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testcases', '0016_managetooldatafilemodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='managetooldatafilemodel',
            name='file_type',
        ),
        migrations.AddField(
            model_name='managetooldatafilemodel',
            name='file_type_id',
            field=models.IntegerField(null=True, verbose_name='文件类型表id'),
        ),
    ]
