# Generated by Django 4.0.3 on 2022-04-15 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='email',
            field=models.EmailField(default='nomail@mail.com', max_length=254),
        ),
        migrations.AddField(
            model_name='contact',
            name='full_name',
            field=models.CharField(default='No Name', max_length=50),
        ),
        migrations.AddField(
            model_name='contact',
            name='message',
            field=models.TextField(default='No Message'),
        ),
        migrations.AddField(
            model_name='contact',
            name='sent_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
