# Generated by Django 3.0.3 on 2020-03-23 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='child',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.Menu'),
        ),
    ]