# Generated by Django 4.2.7 on 2023-12-14 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('woocommerce_integration', '0012_product_order_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(blank=True, to='woocommerce_integration.product'),
        ),
    ]
