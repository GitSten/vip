# Generated by Django 4.2.7 on 2023-12-10 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('woocommerce_integration', '0005_order_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='synced',
            field=models.BooleanField(default=False),
        ),
    ]
