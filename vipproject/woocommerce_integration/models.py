# woocommerce_integration/models.py
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.IntegerField(unique=True)
    customer_name = models.CharField(max_length=255, db_index=True)
    order_date = models.DateTimeField(auto_now_add=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    gift = models.BooleanField(default=False)
    email_notification_sent = models.BooleanField(default=False)
    processed = models.BooleanField(default=False, db_index=True)
    synced = models.BooleanField(default=False)
    total_amount_sum_notified = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    last_notification_date = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

    def mark_as_processed(self):
        self.processed = True
        self.save()

    def __str__(self):
        return f"{self.customer_name} - Tellimuse nr {self.order_id}   Kuupäev {self.order_date}"

    class Meta:
        ordering = ['-order_date']  # Order by date in descending order by default
