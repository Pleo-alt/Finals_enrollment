# Generated by Django 5.1.4 on 2024-12-15 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0023_excelfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='enrollment_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
