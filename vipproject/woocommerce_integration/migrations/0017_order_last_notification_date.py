# Generated by Django 4.2.7 on 2023-12-24 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('woocommerce_integration', '0016_remove_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='last_notification_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]