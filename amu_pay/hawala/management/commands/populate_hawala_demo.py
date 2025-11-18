from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from hawala.models import HawalaTransaction, HawalaReceipt
from saraf_account.models import SarafAccount, SarafEmployee
from currency.models import Currency


class Command(BaseCommand):
    help = 'Populate hawala transactions with demo data for testing filters and endpoints'

    def add_arguments(self, parser):
        parser.add_argument(
            '--saraf-id',
            type=int,
            help='Saraf ID to create demo transactions for (if not provided, uses first available saraf)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo transactions before creating new ones',
        )

    def handle(self, *args, **options):
        saraf_id = options.get('saraf_id')
        clear = options.get('clear')

        # Get or find saraf account
        if saraf_id:
            try:
                saraf = SarafAccount.objects.get(saraf_id=saraf_id)
            except SarafAccount.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Saraf with ID {saraf_id} not found'))
                return
        else:
            saraf = SarafAccount.objects.filter(is_active=True).first()
            if not saraf:
                self.stdout.write(self.style.ERROR('No active Saraf account found. Please create one first.'))
                return

        self.stdout.write(self.style.SUCCESS(f'Using Saraf: {saraf.full_name} (ID: {saraf.saraf_id})'))

        # Clear existing demo transactions if requested
        if clear:
            count = HawalaTransaction.objects.filter(sender_exchange=saraf).count()
            HawalaTransaction.objects.filter(sender_exchange=saraf).delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing hawala transactions'))

        # Get employees if exist
        employees = list(SarafEmployee.objects.filter(saraf_account=saraf, is_active=True))
        if not employees:
            self.stdout.write(self.style.WARNING('No employees found. Creating demo employee for testing...'))
            try:
                from saraf_account.models import DEFAULT_EMPLOYEE_PERMISSIONS
                import hashlib
                demo_employee = SarafEmployee.objects.create(
                    saraf_account=saraf,
                    username='hawala_employee',
                    full_name='Hawala Demo Employee',
                    password_hash=hashlib.sha256('password123'.encode()).hexdigest(),
                    permissions=DEFAULT_EMPLOYEE_PERMISSIONS,
                    is_active=True
                )
                employees = [demo_employee]
                self.stdout.write(self.style.SUCCESS(f'✓ Created demo employee: {demo_employee.full_name}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not create demo employee: {str(e)}'))

        # Get or create currencies
        try:
            usd = Currency.objects.get(currency_code='USD')
            afn = Currency.objects.get(currency_code='AFN')
            eur = Currency.objects.get(currency_code='EUR')
        except Currency.DoesNotExist:
            self.stdout.write(self.style.ERROR('Required currencies (USD, AFN, EUR) not found. Please create them first.'))
            return

        # Get other sarafs for internal transactions
        other_sarafs = list(SarafAccount.objects.filter(is_active=True).exclude(saraf_id=saraf.saraf_id))
        
        now = timezone.now()

        # Demo data structure: (hawala_num, sender, sender_ph, receiver, receiver_ph, amount, currency, fee, 
        #                        dest_name, dest_addr, dest_uses_app, dest_id, status, mode, days_ago, notes, emp_type)
        demo_transactions = [
            # PENDING TRANSACTIONS (Today)
            ("HW001", "Ahmad Karimi", "+93701234567", "Hassan Ali", None, 1000, usd, 20, 
             "Kabul Money Exchange", "Shar-e-Naw, Kabul", True, other_sarafs[0].saraf_id if other_sarafs else None,
             "pending", "internal", 0, "Regular transfer to Kabul", "employee"),
            
            ("HW002", "Sara Noori", "+93702345678", "Fatima Aziz", None, 50000, afn, 500,
             "Herat Exchange", "Main Street, Herat", True, other_sarafs[1].saraf_id if len(other_sarafs) > 1 else other_sarafs[0].saraf_id if other_sarafs else None,
             "pending", "internal", 0, "Family support transfer", "employee"),
            
            ("HW003", "Mohammad Sharif", "+93703456789", "Ali Reza", None, 500, eur, 10,
             "Kandahar Financial Services", "Airport Road, Kandahar", False, None,
             "pending", "external_sender", 0, "External transfer - no app at destination", "saraf"),
            
            # SENT TRANSACTIONS (Yesterday)
            ("HW004", "Laila Hussain", "+93704567890", "Zainab Khan", None, 2000, usd, 40,
             "Mazar Exchange", "Blue Mosque Area, Mazar", True, other_sarafs[0].saraf_id if other_sarafs else None,
             "sent", "internal", 1, "Business payment sent", "employee"),
            
            ("HW005", "Omar Abdullah", "+93705678901", "Parwana Ltd", None, 75000, afn, 750,
             "Jalalabad Money Transfer", "City Center, Jalalabad", True, other_sarafs[1].saraf_id if len(other_sarafs) > 1 else other_sarafs[0].saraf_id if other_sarafs else None,
             "sent", "internal", 1, "Contract payment", "employee"),
            
            # RECEIVED TRANSACTIONS (Last week)
            ("HW006", "Nasir Shah", "+93706789012", "Jawid Ahmad", "+93791234567", 1500, usd, 30,
             "Ghazni Exchange House", "Main Market, Ghazni", True, other_sarafs[0].saraf_id if other_sarafs else None,
             "received", "internal", 3, "Received and verified", "employee"),
            
            ("HW007", "Mariam Aziz", "+93707890123", "Shabnam Ali", "+93792345678", 100000, afn, 1000,
             "Balkh Money Services", "City Square, Balkh", True, other_sarafs[1].saraf_id if len(other_sarafs) > 1 else other_sarafs[0].saraf_id if other_sarafs else None,
             "received", "internal", 4, "Payment received for goods", "employee"),
            
            ("HW008", "Rahmat Khan", "+93708901234", "Farid Hassan", "+93793456789", 800, eur, 15,
             "Kunduz Transfer Center", "North Street, Kunduz", False, None,
             "received", "external_receiver", 5, "External hawala received", "saraf"),
            
            # COMPLETED TRANSACTIONS (Last 2 weeks)
            ("HW009", "Hamid Reza", "+93709012345", "Anwar Saeed", "+93794567890", 3000, usd, 60,
             "Nangarhar Exchange", "University Road, Nangarhar", True, other_sarafs[0].saraf_id if other_sarafs else None,
             "completed", "internal", 8, "Transaction completed successfully", "employee"),
            
            ("HW010", "Zakia Amiri", "+93700123456", "Noor Ahmad", "+93795678901", 120000, afn, 1200,
             "Badakhshan Financial", "Main Road, Badakhshan", True, other_sarafs[1].saraf_id if len(other_sarafs) > 1 else other_sarafs[0].saraf_id if other_sarafs else None,
             "completed", "internal", 10, "Rent payment completed", "employee"),
            
            ("HW011", "Khalil Ibrahim", "+93701112222", "Rashid Ali", "+93796789012", 1200, eur, 25,
             "Baghlan Money Transfer", "City Center, Baghlan", False, None,
             "completed", "external_sender", 12, "External transfer completed", "saraf"),
            
            # COMPLETED TRANSACTIONS (Last month)
            ("HW012", "Roya Karimi", "+93702223333", "Samir Hassan", "+93797890123", 5000, usd, 100,
             "Takhar Exchange Services", "Main Market, Takhar", True, other_sarafs[0].saraf_id if other_sarafs else None,
             "completed", "internal", 18, "Large transfer completed", "employee"),
            
            ("HW013", "Fawad Nazari", "+93703334444", "Latif Khan", "+93798901234", 200000, afn, 2000,
             "Panjshir Money House", "Valley Road, Panjshir", True, other_sarafs[1].saraf_id if len(other_sarafs) > 1 else other_sarafs[0].saraf_id if other_sarafs else None,
             "completed", "internal", 22, "Monthly settlement", "saraf"),
            
            ("HW014", "Samira Walid", "+93704445555", "Hamida Noori", "+93799012345", 900, eur, 20,
             "Kapisa Transfer Point", "North Area, Kapisa", False, None,
             "completed", "external_receiver", 25, "External hawala completed", "employee"),
            
            # MORE RECENT TRANSACTIONS (This week)
            ("HW015", "Navid Akbari", "+93705556666", "Sohrab Ali", None, 1800, usd, 35,
             "Parwan Exchange", "Highway Road, Parwan", True, other_sarafs[0].saraf_id if other_sarafs else None,
             "pending", "internal", 2, "Urgent transfer request", "employee"),
            
            ("HW016", "Gulnaz Fahim", "+93706667777", "Wahid Ahmadi", None, 85000, afn, 850,
             "Logar Money Services", "Downtown, Logar", False, None,
             "pending", "external_sender", 2, "Transfer to external partner", "saraf"),
            
            ("HW017", "Tariq Mansoor", "+93707778888", "Habib Rahman", "+93700111222", 2500, usd, 50,
             "Wardak Financial Center", "City Center, Wardak", True, other_sarafs[1].saraf_id if len(other_sarafs) > 1 else other_sarafs[0].saraf_id if other_sarafs else None,
             "sent", "internal", 3, "Business transaction sent", "employee"),
            
            ("HW018", "Najiba Safi", "+93708889999", "Rahim Karim", "+93701222333", 150000, afn, 1500,
             "Bamyan Transfer Hub", "Tourist Area, Bamyan", True, other_sarafs[0].saraf_id if other_sarafs else None,
             "received", "internal", 4, "Tourism payment received", "employee"),
            
            # OLDER COMPLETED TRANSACTIONS (1-2 months ago)
            ("HW019", "Basir Yusuf", "+93709990000", "Shafiq Azimi", "+93702333444", 4500, usd, 90,
             "Ghor Exchange House", "Main Street, Ghor", True, other_sarafs[1].saraf_id if len(other_sarafs) > 1 else other_sarafs[0].saraf_id if other_sarafs else None,
             "completed", "internal", 35, "Old completed transfer", "saraf"),
            
            ("HW020", "Nargis Faizi", "+93700001111", "Zahir Shah", "+93703444555", 180000, afn, 1800,
             "Zabul Money Exchange", "Market Area, Zabul", False, None,
             "completed", "external_sender", 40, "Historical external transfer", "employee"),
        ]

        created_count = 0
        completed_count = 0
        pending_count = 0
        sent_count = 0
        received_count = 0
        
        for trans_data in demo_transactions:
            (hawala_num, sender, sender_ph, receiver, receiver_ph, amount, currency, fee,
             dest_name, dest_addr, dest_uses_app, dest_id, status_val, mode_val, 
             days_ago, notes, emp_type) = trans_data
            
            # Calculate transaction date
            transaction_date = now - timedelta(days=days_ago)
            
            # Determine employee
            if emp_type == 'employee' and employees:
                employee_index = created_count % len(employees)
                employee = employees[employee_index]
            else:
                employee = None
            
            try:
                # Create transaction
                hawala = HawalaTransaction.objects.create(
                    hawala_number=hawala_num,
                    sender_name=sender,
                    sender_phone=sender_ph,
                    receiver_name=receiver,
                    receiver_phone=receiver_ph,
                    amount=Decimal(str(amount)),
                    currency=currency,
                    transfer_fee=Decimal(str(fee)),
                    sender_exchange=saraf,
                    sender_exchange_name=saraf.exchange_name or saraf.full_name,
                    destination_exchange_id=dest_id,
                    destination_exchange_name=dest_name,
                    destination_exchange_address=dest_addr,
                    destination_saraf_uses_app=dest_uses_app,
                    status=status_val,
                    mode=mode_val,
                    notes=notes,
                    created_by_employee=employee,
                )
                
                # Update created_at to match transaction date
                HawalaTransaction.objects.filter(hawala_number=hawala_num).update(created_at=transaction_date)
                
                # Set appropriate timestamps based on status
                if status_val == 'sent':
                    hawala.sent_at = transaction_date + timedelta(hours=1)
                    hawala.save(update_fields=['sent_at'])
                    sent_count += 1
                elif status_val == 'received':
                    hawala.sent_at = transaction_date + timedelta(hours=1)
                    hawala.received_at = transaction_date + timedelta(hours=2)
                    hawala.received_by_employee = employee
                    hawala.save(update_fields=['sent_at', 'received_at', 'received_by_employee'])
                    received_count += 1
                elif status_val == 'completed':
                    hawala.sent_at = transaction_date + timedelta(hours=1)
                    hawala.received_at = transaction_date + timedelta(hours=2)
                    hawala.completed_at = transaction_date + timedelta(hours=3)
                    hawala.received_by_employee = employee
                    hawala.save(update_fields=['sent_at', 'received_at', 'completed_at', 'received_by_employee'])
                    
                    # Generate receipt for completed transactions
                    try:
                        receipt = HawalaReceipt.objects.create(
                            hawala_transaction=hawala,
                            generated_by_employee=employee
                        )
                        # Update receipt generated_at to match completion time
                        HawalaReceipt.objects.filter(receipt_id=receipt.receipt_id).update(
                            generated_at=hawala.completed_at
                        )
                    except:
                        pass
                    
                    completed_count += 1
                elif status_val == 'pending':
                    pending_count += 1
                
                created_count += 1
                
                # Status emoji
                status_emoji = {
                    'pending': '⏳',
                    'sent': '📤',
                    'received': '📥',
                    'completed': '✅'
                }.get(status_val, '📝')
                
                self.stdout.write(
                    self.style.SUCCESS(f'{status_emoji} Created: {hawala_num} - {sender} → {receiver} ({amount} {currency.currency_code}) [{status_val}]')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to create hawala {hawala_num}: {str(e)}')
                )

        # Summary statistics
        internal_count = HawalaTransaction.objects.filter(sender_exchange=saraf, mode='internal').count()
        external_sender_count = HawalaTransaction.objects.filter(sender_exchange=saraf, mode='external_sender').count()
        external_receiver_count = HawalaTransaction.objects.filter(sender_exchange=saraf, mode='external_receiver').count()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully created {created_count} demo hawala transactions!')
        )
        self.stdout.write(self.style.SUCCESS(f'\n📊 Transaction Statistics:'))
        self.stdout.write(f'  • Status Breakdown:')
        self.stdout.write(f'    - Pending: {pending_count} transactions')
        self.stdout.write(f'    - Sent: {sent_count} transactions')
        self.stdout.write(f'    - Received: {received_count} transactions')
        self.stdout.write(f'    - Completed: {completed_count} transactions')
        
        self.stdout.write(f'  • Mode Breakdown:')
        self.stdout.write(f'    - Internal (both use app): {internal_count} transactions')
        self.stdout.write(f'    - External Sender (only sender uses app): {external_sender_count} transactions')
        self.stdout.write(f'    - External Receiver (only receiver uses app): {external_receiver_count} transactions')
        
        if employees:
            self.stdout.write(f'  • Employee Transactions:')
            for emp in employees:
                emp_count = HawalaTransaction.objects.filter(
                    sender_exchange=saraf,
                    created_by_employee=emp
                ).count()
                self.stdout.write(f'    - {emp.full_name}: {emp_count} transactions')
        
        self.stdout.write(self.style.SUCCESS(f'\n🧪 Test the following endpoints:'))
        self.stdout.write('\n  📤 Send Hawala:')
        self.stdout.write('    POST /api/hawala/send/')
        
        self.stdout.write('\n  📥 Receive Hawala:')
        self.stdout.write('    GET /api/hawala/receive/  (List pending/sent hawalas)')
        self.stdout.write('    GET /api/hawala/receive/<hawala_number>/')
        self.stdout.write('    PATCH /api/hawala/receive/<hawala_number>/')
        
        self.stdout.write('\n  📋 History & Management:')
        self.stdout.write('    GET /api/hawala/history/')
        self.stdout.write('    GET /api/hawala/list-all/')
        self.stdout.write('    PATCH /api/hawala/status/<hawala_number>/')
        
        self.stdout.write('\n  📊 Statistics:')
        self.stdout.write('    GET /api/hawala/statistics/')
        
        self.stdout.write('\n  🧾 Receipts:')
        self.stdout.write('    GET /api/hawala/receipt/<hawala_number>/')
        self.stdout.write('    POST /api/hawala/generate-receipt/<hawala_number>/')
        
        self.stdout.write(self.style.WARNING(f'\n  🔍 Example Filters:'))
        self.stdout.write('    GET /api/hawala/history/?status=completed')
        self.stdout.write('    GET /api/hawala/history/?mode=internal')
        self.stdout.write('    GET /api/hawala/history/?currency=USD')
        self.stdout.write('    GET /api/hawala/history/?start_date=2025-01-01&end_date=2025-01-31')
        
        self.stdout.write(self.style.WARNING(f'\n  📝 Test with these hawala numbers:'))
        self.stdout.write(f'    - Pending: HW001, HW002, HW003')
        self.stdout.write(f'    - Sent: HW004, HW005')
        self.stdout.write(f'    - Received: HW006, HW007, HW008')
        self.stdout.write(f'    - Completed: HW009, HW010, HW011')

