# Generated by Django 4.2.6 on 2023-10-28 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_userprofile_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='region',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]