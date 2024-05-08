# Generated by Django 5.0.4 on 2024-05-07 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_subscription_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='created_at',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='price',
            field=models.FloatField(default='1'),
            preserve_default=False,
        ),
    ]
