# Generated by Django 5.1.7 on 2025-03-07 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "stock_app",
            "0002_remove_portfolio_updated_at_transaction_limit_price_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="stock",
            name="sector",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
