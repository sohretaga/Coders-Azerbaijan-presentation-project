# Generated by Django 4.0.3 on 2022-03-27 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_product_amount_product_available_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='amount',
        ),
    ]