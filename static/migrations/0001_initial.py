# Generated by Django 2.0 on 2017-12-21 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Static',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the pair.', max_length=200)),
                ('value', models.TextField(help_text='The value of the pair.')),
            ],
        ),
    ]
