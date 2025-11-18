from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import ExchangeTransaction
from saraf_account.models import SarafAccount, SarafEmployee


class ExchangeTransactionModelTest(TestCase):
    """Test cases for ExchangeTransaction model"""
    
    def setUp(self):
        """Set up test data"""
        self.saraf_account = SarafAccount.objects.create(
            saraf_id=1,
            full_name="Test Saraf",
            email_or_whatsapp_number="test@example.com",
            exchange_name="Test Exchange",
            amu_pay_code="TEST001",
            province="Kabul"
        )
        
        self.employee = SarafEmployee.objects.create(
            saraf_account=self.saraf_account,
            username="test_employee",
            full_name="Test Employee"
        )
    
    def test_exchange_transaction_creation(self):
        """Test creating an exchange transaction"""
        transaction = ExchangeTransaction.objects.create(
            name="Test Customer",
            transaction_type="customer",
            sell_currency="USD",
            sell_amount=Decimal("100.00"),
            buy_currency="AFN",
            buy_amount=Decimal("7550.00"),
            rate=Decimal("75.50"),
            saraf_account=self.saraf_account,
            performed_by_employee=self.employee
        )
        
        self.assertEqual(transaction.name, "Test Customer")
        self.assertEqual(transaction.sell_currency, "USD")
        self.assertEqual(transaction.buy_currency, "AFN")
        self.assertEqual(transaction.rate, Decimal("75.50"))
    
    def test_currency_code_validation(self):
        """Test currency code validation"""
        with self.assertRaises(Exception):
            ExchangeTransaction.objects.create(
                name="Test Customer",
                transaction_type="customer",
                sell_currency="US",  # Invalid: only 2 characters
                sell_amount=Decimal("100.00"),
                buy_currency="AFN",
                buy_amount=Decimal("7550.00"),
                rate=Decimal("75.50"),
                saraf_account=self.saraf_account
            )
    
    def test_same_currency_validation(self):
        """Test validation for same sell and buy currency"""
        with self.assertRaises(Exception):
            ExchangeTransaction.objects.create(
                name="Test Customer",
                transaction_type="customer",
                sell_currency="USD",
                sell_amount=Decimal("100.00"),
                buy_currency="USD",  # Same as sell currency
                buy_amount=Decimal("100.00"),
                rate=Decimal("1.00"),
                saraf_account=self.saraf_account
            )
    
    def test_negative_amount_validation(self):
        """Test validation for negative amounts"""
        with self.assertRaises(Exception):
            ExchangeTransaction.objects.create(
                name="Test Customer",
                transaction_type="customer",
                sell_currency="USD",
                sell_amount=Decimal("-100.00"),  # Negative amount
                buy_currency="AFN",
                buy_amount=Decimal("7550.00"),
                rate=Decimal("75.50"),
                saraf_account=self.saraf_account
            )
    
    def test_get_performed_by_info(self):
        """Test getting performed by information"""
        transaction = ExchangeTransaction.objects.create(
            name="Test Customer",
            transaction_type="customer",
            sell_currency="USD",
            sell_amount=Decimal("100.00"),
            buy_currency="AFN",
            buy_amount=Decimal("7550.00"),
            rate=Decimal("75.50"),
            saraf_account=self.saraf_account,
            performed_by_employee=self.employee
        )
        
        performed_by_info = transaction.get_performed_by_info()
        self.assertEqual(performed_by_info['type'], 'employee')
        self.assertEqual(performed_by_info['id'], self.employee.employee_id)
        self.assertEqual(performed_by_info['name'], 'Test Employee')
    
    def test_calculate_rate(self):
        """Test rate calculation"""
        transaction = ExchangeTransaction.objects.create(
            name="Test Customer",
            transaction_type="customer",
            sell_currency="USD",
            sell_amount=Decimal("100.00"),
            buy_currency="AFN",
            buy_amount=Decimal("7550.00"),
            rate=Decimal("75.50"),
            saraf_account=self.saraf_account
        )
        
        calculated_rate = transaction.calculate_rate()
        self.assertEqual(calculated_rate, Decimal("75.50"))


class ExchangeTransactionViewTest(TestCase):
    """Test cases for ExchangeTransaction views"""
    
    def setUp(self):
        """Set up test data"""
        self.saraf_account = SarafAccount.objects.create(
            saraf_id=1,
            full_name="Test Saraf",
            email_or_whatsapp_number="test@example.com",
            exchange_name="Test Exchange",
            amu_pay_code="TEST001",
            province="Kabul"
        )
        
        self.employee = SarafEmployee.objects.create(
            saraf_account=self.saraf_account,
            username="test_employee",
            full_name="Test Employee"
        )
    
    def test_exchange_transaction_list_view(self):
        """Test exchange transaction list view"""
        # This would require proper authentication setup
        # For now, just test that the view exists
        from .views import ExchangeTransactionListView
        self.assertTrue(ExchangeTransactionListView)
    
    def test_exchange_transaction_create_view(self):
        """Test exchange transaction create view"""
        from .views import ExchangeTransactionCreateView, ExchangeTransactionCreateWithBalanceView
        self.assertTrue(ExchangeTransactionCreateView)
        self.assertTrue(ExchangeTransactionCreateWithBalanceView)
    
    def test_exchange_transaction_detail_view(self):
        """Test exchange transaction detail view"""
        from .views import ExchangeTransactionDetailView
        self.assertTrue(ExchangeTransactionDetailView)
