# Generated by Django 4.2.7 on 2023-12-11 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('woocommerce_integration', '0009_delete_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_item',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
