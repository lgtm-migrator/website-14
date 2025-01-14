# Generated by Django 3.0.4 on 2020-03-05 13:56

from django.db import migrations, models

import phonedb.models


class Migration(migrations.Migration):

    dependencies = [
        ("phonedb", "0002_auto_20170407_1451"),
    ]

    operations = [
        migrations.AlterField(
            model_name="connection",
            name="name",
            field=models.CharField(max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name="feature",
            name="name",
            field=models.CharField(max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name="phone",
            name="name",
            field=models.CharField(
                db_index=True,
                help_text="Phone name, please exclude vendor name.",
                max_length=250,
                validators=[phonedb.models.phone_name_validator],
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="name",
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
