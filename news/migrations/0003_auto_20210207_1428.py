# Generated by Django 3.1.6 on 2021-02-07 14:28

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_auto_20161214_0849"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entry",
            name="pub_date",
            field=models.DateTimeField(
                db_index=True,
                default=datetime.datetime.today,
                verbose_name="Date posted",
            ),
        ),
    ]
