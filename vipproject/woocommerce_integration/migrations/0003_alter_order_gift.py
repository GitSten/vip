# Generated by Django 4.2.7 on 2023-12-04 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('woocommerce_integration', '0002_order_gift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='gift',
            field=models.BooleanField(default=False),
        ),
    ]