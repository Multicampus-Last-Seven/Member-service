# Generated by Django 3.1.7 on 2021-05-28 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0003_serials_is_alive'),
    ]

    operations = [
        migrations.AddField(
            model_name='serials',
            name='location',
            field=models.CharField(default='null', max_length=255),
        ),
    ]
