# Generated by Django 5.2.3 on 2025-07-03 21:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratorium', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pengembalian',
            name='peminjaman',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laboratorium.peminjaman'),
        ),
    ]
