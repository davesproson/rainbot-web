# Generated by Django 3.0.3 on 2020-05-03 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rainbot',
            name='battery',
            field=models.FloatField(default=4.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rainbot',
            name='name',
            field=models.CharField(default='Zippy', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rainbot',
            name='wifi',
            field=models.IntegerField(default=-50),
            preserve_default=False,
        ),
    ]
