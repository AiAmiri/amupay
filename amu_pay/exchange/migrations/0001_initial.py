# Generated manually to fix missing table issue

from django.db import migrations, models
import django.core.validators
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('saraf_account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, help_text='Name of the exchange partner or customer')),
                ('transaction_type', models.CharField(choices=[('person', 'Person'), ('exchanger', 'Exchanger'), ('customer', 'Customer')], default='customer', max_length=20, help_text='Type of exchange transaction')),
                ('sell_currency', models.CharField(max_length=3, help_text='Currency code being sold (e.g. USD, AFN)')),
                ('sell_amount', models.DecimalField(decimal_places=2, default=0, help_text='Amount of currency being sold', max_digits=15)),
                ('buy_currency', models.CharField(max_length=3, help_text='Currency code being bought (e.g. USD, AFN)')),
                ('buy_amount', models.DecimalField(decimal_places=2, default=0, help_text='Amount of currency being bought', max_digits=15)),
                ('rate', models.DecimalField(decimal_places=4, help_text='Exchange rate (buy_amount per 1 sell_amount)', max_digits=10)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the transaction', null=True)),
                ('transaction_date', models.DateTimeField(default=timezone.now, help_text='Date and time of the transaction')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('performed_by_saraf', models.ForeignKey(blank=True, help_text='Saraf who performed the transaction', null=True, on_delete=models.SET_NULL, related_name='performed_exchanges', to='saraf_account.sarafaccount')),
                ('performed_by_employee', models.ForeignKey(blank=True, help_text='Employee who performed the transaction', null=True, on_delete=models.SET_NULL, related_name='performed_exchanges', to='saraf_account.sarafemployee')),
                ('saraf_account', models.ForeignKey(help_text='Saraf account performing the exchange', on_delete=models.CASCADE, related_name='exchange_transactions', to='saraf_account.sarafaccount')),
            ],
            options={
                'verbose_name': 'Exchange Transaction',
                'verbose_name_plural': 'Exchange Transactions',
                'ordering': ['-transaction_date', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='exchangetransaction',
            index=models.Index(fields=['saraf_account', 'transaction_date'], name='exchange_ex_saraf_a_123456_idx'),
        ),
        migrations.AddIndex(
            model_name='exchangetransaction',
            index=models.Index(fields=['sell_currency', 'buy_currency'], name='exchange_ex_sell_cu_234567_idx'),
        ),
        migrations.AddIndex(
            model_name='exchangetransaction',
            index=models.Index(fields=['transaction_type'], name='exchange_ex_transac_345678_idx'),
        ),
        migrations.AddIndex(
            model_name='exchangetransaction',
            index=models.Index(fields=['transaction_date'], name='exchange_ex_transac_456789_idx'),
        ),
        migrations.AddIndex(
            model_name='exchangetransaction',
            index=models.Index(fields=['name'], name='exchange_ex_name_567890_idx'),
        ),
    ]