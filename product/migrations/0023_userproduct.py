# Generated by Django 4.0.3 on 2022-04-16 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_product_sale'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('main_image', models.ImageField(upload_to='static/product_images/%Y/%m/%d/')),
                ('detail', models.TextField()),
                ('keywords', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=1000)),
                ('price', models.FloatField()),
                ('sale', models.IntegerField(blank=True, null=True, verbose_name='Sale (%)')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.category')),
            ],
        ),
    ]