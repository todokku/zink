# Generated by Django 2.0.3 on 2018-03-27 20:30

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reading', '0002_auto_20180326_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='text',
            name='read',
        ),
        migrations.AddField(
            model_name='text',
            name='completed',
            field=models.BooleanField(
                default=False,
                help_text='Read the text completely.'
            ),
        ),
        migrations.AddField(
            model_name='text',
            name='finished_reading',
            field=models.DateTimeField(
                blank=True,
                default=django.utils.timezone.now,
                help_text='Date and time when I finished reading this text.',
                null=True,
                verbose_name='finished_reading'
            ),
        ),
        migrations.AddField(
            model_name='text',
            name='started_reading',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text='Date and time when I started to read this text.',
                verbose_name='started_reading'
            ),
        ),
        migrations.AlterField(
            model_name='text',
            name='created',
            field=models.DateTimeField(
                blank=True,
                default=django.utils.timezone.now,
                help_text='Date and time when this text came into my hands.',
                null=True,
                verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='text',
            name='ranking',
            field=models.IntegerField(
                help_text='Its rank - how good was it?',
                validators=[django.core.validators.MaxValueValidator(10),
                            django.core.validators.MinValueValidator(-1)]
            ),
        ),
        migrations.AlterField(
            model_name='text',
            name='topics',
            field=models.ManyToManyField(
                blank=True,
                help_text='The topic this is about.',
                to='reading.Topic'
            ),
        ),
        migrations.AlterField(
            model_name='text',
            name='type',
            field=models.ManyToManyField(
                blank=True,
                help_text='The type of reading material.',
                to='reading.Type'
            ),
        ),
    ]
