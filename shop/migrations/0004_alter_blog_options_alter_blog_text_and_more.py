# Generated by Django 4.2.4 on 2023-10-31 10:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0003_blog'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='blog',
            name='text',
            field=models.TextField(max_length=1860),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, choices=[('F', 'Fantasy'), ('D', 'Detective'), ('H', 'Horror'), ('A', 'Adults'), ('P', 'Poetry'), ('DR', 'Drama'), ('HIS', 'History'), ('C', 'Comedy')], max_length=3, null=True),
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'product')},
            },
        ),
    ]
