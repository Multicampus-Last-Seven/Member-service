# Generated by Django 3.1.7 on 2021-05-30 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0005_auto_20210530_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iot',
            name='is_alive',
            field=models.BooleanField(default=False, null=True),
        ),
    ]