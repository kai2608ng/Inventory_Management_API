# Generated by Django 4.1.3 on 2022-12-30 04:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('max_capacity', models.PositiveSmallIntegerField(default=0)),
                ('current_capacity', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'db_table': 'material',
            },
        ),
        migrations.CreateModel(
            name='MaterialQuantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=0)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='material_material_quantity', to='material.material')),
            ],
            options={
                'db_table': 'material_quantity',
            },
        ),
    ]