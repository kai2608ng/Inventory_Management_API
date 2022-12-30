# Generated by Django 4.1.3 on 2022-12-30 04:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_entries', to='store.store'),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('name', 'store')},
        ),
    ]
