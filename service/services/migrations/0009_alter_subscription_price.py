# Generated by Django 5.0.4 on 2024-05-08 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_alter_subscription_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
