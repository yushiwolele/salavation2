# Generated by Django 3.2.16 on 2024-05-24 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testcases', '0014_ranscriptresultmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptconfig',
            name='name',
            field=models.CharField(max_length=300, verbose_name='脚本测试套件名字'),
        ),
    ]