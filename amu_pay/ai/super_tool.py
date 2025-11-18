"""
SuperTool - Django-based LangChain tool for collecting and summarizing Saraf data
Provides comprehensive data aggregation for authenticated Saraf accounts with security validation.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

# Import all relevant models
from saraf_account.models import SarafAccount, SarafEmployee
from exchange.models import ExchangeTransaction
from transaction.models import Transaction
from saraf_balance.models import SarafBalance
from currency.models import Currency, SarafSupportedCurrency
from saraf_post.models import SarafPost
from msg.models import Conversation, Message
from saraf_social.models import SarafLike, SarafComment
from hawala.models import HawalaTransaction
from saraf_create_accounts.models import SarafCustomerAccount, CustomerTransaction

# Configure logging
logger = logging.getLogger(__name__)


class SuperTool:
    """
    LangChain tool for collecting and summarizing Saraf data with authentication.
    
    This tool safely queries all relevant models for a specific Saraf after
    JWT verification and saraf_id validation. It aggregates results and returns
    structured JSON for LLM context.
    """
    
    def __init__(self, authenticated_user=None):
        """
        Initialize SuperTool with authenticated user context.
        
        Args:
            authenticated_user: CustomUser object from JWT authentication
        """
        self.authenticated_user = authenticated_user
        self.saraf_id = None
        self.user_type = None
        
        if authenticated_user:
            # Extract saraf_id from token - ensure it's an integer
            saraf_id = getattr(authenticated_user, 'saraf_id', None)
            if saraf_id is not None:
                # Ensure saraf_id is an integer, not a string or object
                if isinstance(saraf_id, (int, str)):
                    try:
                        self.saraf_id = int(saraf_id)
                    except (ValueError, TypeError):
                        logger.error(f"Invalid saraf_id type: {type(saraf_id)} = {saraf_id}")
                        self.saraf_id = None
                else:
                    logger.error(f"Unexpected saraf_id type: {type(saraf_id)} = {saraf_id}")
                    self.saraf_id = None
            else:
                logger.warning("No saraf_id found in authenticated_user")
            
            self.user_type = getattr(authenticated_user, 'user_type', None)
    
    def verify_saraf_access(self, saraf_id: int) -> Dict[str, Any]:
        """
        Verify that the authenticated user has access to the specified saraf_id.
        
        Args:
            saraf_id: The saraf_id (integer) to verify access for
            
        Returns:
            Dict with verification result and error message if any
        """
        try:
            # Ensure saraf_id is an integer
            if not isinstance(saraf_id, int):
                try:
                    saraf_id = int(saraf_id)
                except (ValueError, TypeError):
                    logger.error(f"Invalid saraf_id type in verify_saraf_access: {type(saraf_id)} = {saraf_id}")
                    return {
                        "success": False,
                        "error": f"Invalid saraf_id type: {type(saraf_id)}"
                    }
            
            # Check if user is authenticated
            if not self.authenticated_user:
                return {
                    "success": False,
                    "error": "Authentication required"
                }
            
            # Verify saraf_id matches authenticated user's saraf_id
            if self.saraf_id != saraf_id:
                logger.warning(f"Unauthorized saraf_id access attempt: {self.saraf_id} trying to access {saraf_id}")
                return {
                    "success": False,
                    "error": "Unauthorized or invalid saraf_id"
                }
            
            # Verify saraf account exists and is active - use saraf_id (integer) for query
            try:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=saraf_id,  # Using integer saraf_id, not name
                    is_active=True
                )
                logger.info(f"Successfully verified access for saraf_id: {saraf_id}")
                return {
                    "success": True,
                    "saraf_account": saraf_account
                }
            except SarafAccount.DoesNotExist:
                logger.warning(f"Saraf account not found or inactive: {saraf_id}")
                return {
                    "success": False,
                    "error": "Saraf account not found or inactive"
                }
                
        except Exception as e:
            logger.error(f"Error verifying saraf access: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Verification error: {str(e)}"
            }
    
    def collect_saraf_profile_data(self, saraf_account: SarafAccount) -> Dict[str, Any]:
        """
        Collect basic Saraf profile information.
        
        Args:
            saraf_account: SarafAccount instance
            
        Returns:
            Dict with profile data
        """
        try:
            return {
                "saraf_id": saraf_account.saraf_id,
                "full_name": saraf_account.full_name,
                "exchange_name": saraf_account.exchange_name,
                "email_or_whatsapp": saraf_account.email_or_whatsapp_number,
                "license_no": saraf_account.license_no,
                "amu_pay_code": saraf_account.amu_pay_code,
                "saraf_address": saraf_account.saraf_address,
                "province": saraf_account.province,
                "is_email_verified": saraf_account.is_email_verified,
                "is_whatsapp_verified": saraf_account.is_whatsapp_verified,
                "created_at": saraf_account.created_at.isoformat(),
                "updated_at": saraf_account.updated_at.isoformat(),
                "is_active": saraf_account.is_active
            }
        except Exception as e:
            logger.error(f"Error collecting saraf profile data: {str(e)}")
            return {"error": f"Profile data collection error: {str(e)}"}
    
    def collect_balance_data(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect Saraf balance information for all currencies.
        
        Args:
            saraf_id: Saraf ID to collect balance data for
            limit: Maximum number of records to return
            
        Returns:
            Dict with balance data
        """
        try:
            balances = SarafBalance.objects.filter(
                saraf_account_id=saraf_id
            ).select_related('currency')[:limit]
            
            balance_data = []
            for balance in balances:
                balance_data.append({
                    "currency_code": balance.currency.currency_code,
                    "currency_name": balance.currency.currency_name,
                    "balance": float(balance.balance),
                    "total_deposits": float(balance.total_deposits),
                    "total_withdrawals": float(balance.total_withdrawals),
                    "transaction_count": balance.transaction_count,
                    "last_updated": balance.last_updated.isoformat()
                })
            
            return {
                "balances": balance_data,
                "total_currencies": len(balance_data)
            }
        except Exception as e:
            logger.error(f"Error collecting balance data: {str(e)}")
            return {"error": f"Balance data collection error: {str(e)}"}
    
    def collect_exchange_transactions(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect recent exchange transactions for the Saraf.
        
        Args:
            saraf_id: Saraf ID to collect exchange transactions for
            limit: Maximum number of records to return
            
        Returns:
            Dict with exchange transaction data
        """
        try:
            transactions = ExchangeTransaction.objects.filter(
                saraf_account_id=saraf_id
            ).select_related('performed_by_saraf', 'performed_by_employee').order_by('-transaction_date')[:limit]
            
            transaction_data = []
            for transaction in transactions:
                try:
                    # Validate transaction is an ExchangeTransaction object
                    if not isinstance(transaction, ExchangeTransaction):
                        logger.warning(f"Unexpected transaction type: {type(transaction)}")
                        continue
                    
                    # Safely access performed_by_saraf - ensure it's an object, not an integer
                    performed_by_saraf_name = None
                    if transaction.performed_by_saraf:
                        if hasattr(transaction.performed_by_saraf, 'full_name'):
                            performed_by_saraf_name = transaction.performed_by_saraf.full_name
                        else:
                            logger.warning(f"performed_by_saraf is not an object: {type(transaction.performed_by_saraf)}")
                    
                    # Safely access performed_by_employee - ensure it's an object, not an integer
                    performed_by_employee_name = None
                    if transaction.performed_by_employee:
                        if hasattr(transaction.performed_by_employee, 'full_name'):
                            performed_by_employee_name = transaction.performed_by_employee.full_name
                        else:
                            logger.warning(f"performed_by_employee is not an object: {type(transaction.performed_by_employee)}")
                    
                    transaction_data.append({
                        "name": getattr(transaction, 'name', 'Unknown'),
                        "transaction_type": getattr(transaction, 'transaction_type', 'Unknown'),
                        "sell_currency": getattr(transaction, 'sell_currency', ''),
                        "sell_amount": float(getattr(transaction, 'sell_amount', 0)),
                        "buy_currency": getattr(transaction, 'buy_currency', ''),
                        "buy_amount": float(getattr(transaction, 'buy_amount', 0)),
                        "rate": float(getattr(transaction, 'rate', 0)),
                        "notes": getattr(transaction, 'notes', '') or "",
                        "transaction_date": transaction.transaction_date.isoformat() if hasattr(transaction, 'transaction_date') and transaction.transaction_date else None,
                        "performed_by_saraf": performed_by_saraf_name,
                        "performed_by_employee": performed_by_employee_name,
                        "created_at": transaction.created_at.isoformat() if hasattr(transaction, 'created_at') and transaction.created_at else None
                    })
                except AttributeError as e:
                    logger.error(f"AttributeError accessing transaction fields: {str(e)}", exc_info=True)
                    continue
                except Exception as e:
                    logger.error(f"Error processing transaction: {str(e)}", exc_info=True)
                    continue
            
            return {
                "exchange_transactions": transaction_data,
                "total_transactions": len(transaction_data)
            }
        except Exception as e:
            logger.error(f"Error collecting exchange transactions: {str(e)}", exc_info=True)
            return {"error": f"Exchange transaction collection error: {str(e)}"}
    
    def collect_deposit_withdrawal_transactions(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect recent deposit and withdrawal transactions for the Saraf.
        
        Args:
            saraf_id: Saraf ID to collect transactions for
            limit: Maximum number of records to return
            
        Returns:
            Dict with transaction data
        """
        try:
            transactions = Transaction.objects.filter(
                saraf_account_id=saraf_id
            ).select_related('currency').order_by('-created_at')[:limit]
            
            transaction_data = []
            for transaction in transactions:
                transaction_data.append({
                    "transaction_id": transaction.transaction_id,
                    "currency_code": transaction.currency.currency_code,
                    "transaction_type": transaction.transaction_type,
                    "amount": float(transaction.amount),
                    "description": transaction.description,
                    "performer_user_type": transaction.performer_user_type,
                    "performer_full_name": transaction.performer_full_name,
                    "performer_employee_name": transaction.performer_employee_name,
                    "balance_before": float(transaction.balance_before),
                    "balance_after": float(transaction.balance_after),
                    "created_at": transaction.created_at.isoformat()
                })
            
            return {
                "deposit_withdrawal_transactions": transaction_data,
                "total_transactions": len(transaction_data)
            }
        except Exception as e:
            logger.error(f"Error collecting deposit/withdrawal transactions: {str(e)}")
            return {"error": f"Transaction collection error: {str(e)}"}
    
    def collect_supported_currencies(self, saraf_id: int) -> Dict[str, Any]:
        """
        Collect currencies supported by the Saraf.
        
        Args:
            saraf_id: Saraf ID to collect supported currencies for
            
        Returns:
            Dict with supported currency data
        """
        try:
            supported_currencies = SarafSupportedCurrency.objects.filter(
                saraf_account_id=saraf_id,
                is_active=True
            ).select_related('currency')
            
            currency_data = []
            for supported_currency in supported_currencies:
                currency_data.append({
                    "currency_code": supported_currency.currency.currency_code,
                    "currency_name": supported_currency.currency.currency_name,
                    "currency_symbol": supported_currency.currency.symbol,
                    "added_at": supported_currency.added_at.isoformat(),
                    "is_active": supported_currency.is_active
                })
            
            return {
                "supported_currencies": currency_data,
                "total_currencies": len(currency_data)
            }
        except Exception as e:
            logger.error(f"Error collecting supported currencies: {str(e)}")
            return {"error": f"Supported currency collection error: {str(e)}"}
    
    def collect_social_data(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect social media data (posts, likes, comments) for the Saraf.
        
        Args:
            saraf_id: Saraf ID to collect social data for
            limit: Maximum number of records to return
            
        Returns:
            Dict with social data
        """
        try:
            # Collect posts
            posts = SarafPost.objects.filter(
                saraf_account_id=saraf_id
            ).order_by('-created_at')[:limit]
            
            posts_data = []
            for post in posts:
                posts_data.append({
                    "post_id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "created_at": post.created_at.isoformat(),
                    "updated_at": post.updated_at.isoformat(),
                    "published_at": post.published_at.isoformat() if post.published_at else None
                })
            
            # Collect likes count
            likes_count = SarafLike.objects.filter(
                saraf_account_id=saraf_id
            ).count()
            
            # Collect comments count
            comments_count = SarafComment.objects.filter(
                saraf_account_id=saraf_id
            ).count()
            
            return {
                "posts": posts_data,
                "total_posts": len(posts_data),
                "total_likes": likes_count,
                "total_comments": comments_count
            }
        except Exception as e:
            logger.error(f"Error collecting social data: {str(e)}")
            return {"error": f"Social data collection error: {str(e)}"}
    
    def collect_customer_accounts(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect customer accounts created by the Saraf.
        
        Args:
            saraf_id: Saraf ID to collect customer accounts for
            limit: Maximum number of records to return
            
        Returns:
            Dict with customer account data
        """
        try:
            customer_accounts = SarafCustomerAccount.objects.filter(
                saraf_account_id=saraf_id
            ).order_by('-created_at')[:limit]
            
            accounts_data = []
            for account in customer_accounts:
                accounts_data.append({
                    "account_id": account.account_id,
                    "customer_name": account.full_name,
                    "customer_phone": account.phone,
                    "account_number": account.account_number,
                    "account_type": account.account_type,
                    "is_active": account.is_active,
                    "created_at": account.created_at.isoformat(),
                    "updated_at": account.updated_at.isoformat()
                })
            
            return {
                "customer_accounts": accounts_data,
                "total_accounts": len(accounts_data)
            }
        except Exception as e:
            logger.error(f"Error collecting customer accounts: {str(e)}")
            return {"error": f"Customer account collection error: {str(e)}"}
    
    def collect_hawala_transactions(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect Hawala (money transfer) transactions for the Saraf.
        
        Args:
            saraf_id: The Saraf account ID
            limit: Maximum number of transactions to retrieve (default: 20)
            
        Returns:
            Dict with Hawala transaction data and statistics
        """
        try:
            # Get all Hawala transactions where this Saraf is sender or receiver
            hawala_transactions = HawalaTransaction.objects.filter(
                models.Q(sender_exchange_id=saraf_id) | models.Q(destination_exchange_id=saraf_id)
            ).select_related(
                'sender_exchange', 'currency'
            ).order_by('-created_at')[:limit]
            
            transactions_list = []
            for transaction in hawala_transactions:
                transactions_list.append({
                    "hawala_number": transaction.hawala_number,
                    "sender": transaction.sender_exchange.full_name if transaction.sender_exchange else "Unknown",
                    "receiver": transaction.destination_exchange_name,
                    "sender_name": transaction.sender_name,
                    "receiver_name": transaction.receiver_name,
                    "amount": float(transaction.amount),
                    "currency": transaction.currency.currency_code,
                    "status": transaction.status,
                    "mode": transaction.mode,
                    "created_at": transaction.created_at.isoformat()
                })
            
            return {
                "hawala_transactions": transactions_list,
                "total_transactions": len(transactions_list)
            }
            
        except Exception as e:
            logger.error(f"Error collecting Hawala transactions: {str(e)}")
            return {"error": f"Hawala transaction collection error: {str(e)}"}
    
    def collect_employees(self, saraf_id: int) -> Dict[str, Any]:
        """
        Collect employees working for the Saraf.
        
        Args:
            saraf_id: The Saraf account ID
            
        Returns:
            Dict with employee data
        """
        try:
            employees = SarafEmployee.objects.filter(
                saraf_account_id=saraf_id
            ).select_related('saraf_account')
            
            employees_list = []
            for emp in employees:
                employees_list.append({
                    "employee_id": emp.employee_id,
                    "username": emp.username,
                    "full_name": emp.full_name,
                    "is_active": emp.is_active
                })
            
            return {
                "employees": employees_list,
                "total_employees": employees.count()
            }
            
        except Exception as e:
            logger.error(f"Error collecting employees: {str(e)}")
            return {"error": f"Employee collection error: {str(e)}"}
    
    def collect_conversations(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect conversations involving the Saraf.
        
        Args:
            saraf_id: The Saraf account ID
            limit: Maximum number of conversations to retrieve (default: 20)
            
        Returns:
            Dict with conversation data
        """
        try:
            conversations = Conversation.objects.filter(
                saraf_participants__saraf_id=saraf_id,
                is_active=True
            ).prefetch_related('saraf_participants', 'normal_user_participants').order_by('-updated_at')[:limit]
            
            conversations_list = []
            for conv in conversations:
                last_message = conv.get_last_message()
                conversations_list.append({
                    "conversation_id": conv.conversation_id,
                    "type": conv.conversation_type,
                    "participants": conv.get_participant_names(),
                    "last_message": last_message.content[:50] if last_message else "No messages",
                    "updated_at": conv.updated_at.isoformat()
                })
            
            return {
                "conversations": conversations_list,
                "total_conversations": conversations.count()
            }
            
        except Exception as e:
            logger.error(f"Error collecting conversations: {str(e)}")
            return {"error": f"Conversation collection error: {str(e)}"}
    
    def collect_messages(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect recent messages sent by the Saraf.
        
        Args:
            saraf_id: The Saraf account ID
            limit: Maximum number of messages to retrieve (default: 20)
            
        Returns:
            Dict with message data
        """
        try:
            messages = Message.objects.filter(
                sender_saraf_id=saraf_id
            ).select_related('conversation').order_by('-created_at')[:limit]
            
            messages_list = []
            for msg in messages:
                messages_list.append({
                    "message_id": msg.message_id,
                    "content": msg.content[:100],
                    "type": msg.message_type,
                    "created_at": msg.created_at.isoformat()
                })
            
            return {
                "messages": messages_list,
                "total_messages": messages.count()
            }
            
        except Exception as e:
            logger.error(f"Error collecting messages: {str(e)}")
            return {"error": f"Message collection error: {str(e)}"}
    
    def collect_customer_transactions(self, saraf_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Collect transactions from customer accounts.
        
        Args:
            saraf_id: The Saraf account ID
            limit: Maximum number of transactions to retrieve (default: 20)
            
        Returns:
            Dict with customer transaction data
        """
        try:
            customer_transactions = CustomerTransaction.objects.filter(
                customer_account__saraf_id=saraf_id
            ).select_related('customer_account', 'currency').order_by('-created_at')[:limit]
            
            transactions_list = []
            for transaction in customer_transactions:
                transactions_list.append({
                    "transaction_id": transaction.transaction_id,
                    "customer": transaction.customer_account.full_name or transaction.customer_account.account_number,
                    "customer_account_number": transaction.customer_account.account_number,
                    "amount": float(transaction.amount),
                    "currency": transaction.currency.currency_code,
                    "transaction_type": transaction.transaction_type,
                    "description": transaction.description,
                    "created_at": transaction.created_at.isoformat()
                })
            
            return {
                "customer_transactions": transactions_list,
                "total_transactions": customer_transactions.count()
            }
            
        except Exception as e:
            logger.error(f"Error collecting customer transactions: {str(e)}")
            return {"error": f"Customer transaction collection error: {str(e)}"}
    
    def collect_all_data(self) -> Dict[str, Any]:
        """
        Collect and aggregate all relevant data for the authenticated Saraf.
        Automatically extracts saraf_id (integer) from the authenticated user's token.
        
        IMPORTANT: All database queries use saraf_id (integer), never saraf name or object.
        The saraf_id is extracted from the JWT access token during authentication.
        
        Returns:
            Structured JSON response with all collected data
        """
        try:
            # Get saraf_id (integer) from authenticated user token
            # This saraf_id is extracted from JWT token, not from database lookup
            if not self.authenticated_user or not self.saraf_id:
                return {
                    "error": "Authentication required - no saraf_id found in token",
                    "saraf_id": None,
                    "timestamp": None
                }
            
            # Ensure saraf_id is an integer (extracted from token)
            saraf_id = int(self.saraf_id) if self.saraf_id is not None else None
            if saraf_id is None:
                return {
                    "error": "Invalid saraf_id in token",
                    "saraf_id": None,
                    "timestamp": None
                }
            
            # Verify access first
            verification_result = self.verify_saraf_access(saraf_id)
            if not verification_result["success"]:
                return {
                    "error": verification_result["error"],
                    "saraf_id": saraf_id,
                    "timestamp": None
                }
            
            saraf_account = verification_result["saraf_account"]
            
            # Collect all data sections
            profile_data = self.collect_saraf_profile_data(saraf_account)
            balance_data = self.collect_balance_data(saraf_id)
            exchange_data = self.collect_exchange_transactions(saraf_id)
            transaction_data = self.collect_deposit_withdrawal_transactions(saraf_id)
            currency_data = self.collect_supported_currencies(saraf_id)
            social_data = self.collect_social_data(saraf_id)
            customer_data = self.collect_customer_accounts(saraf_id)
            hawala_data = self.collect_hawala_transactions(saraf_id)
            employees_data = self.collect_employees(saraf_id)
            conversations_data = self.collect_conversations(saraf_id)
            messages_data = self.collect_messages(saraf_id)
            customer_transactions_data = self.collect_customer_transactions(saraf_id)
            
            # Aggregate all data
            aggregated_data = {
                "saraf_id": saraf_id,
                "timestamp": saraf_account.updated_at.isoformat(),
                "profile": profile_data,
                "balances": balance_data,
                "exchange_transactions": exchange_data,
                "deposit_withdrawal_transactions": transaction_data,
                "supported_currencies": currency_data,
                "social_data": social_data,
                "customer_accounts": customer_data,
                "hawala_transactions": hawala_data,
                "employees": employees_data,
                "conversations": conversations_data,
                "messages": messages_data,
                "customer_transactions": customer_transactions_data,
                "summary": {
                    "total_currencies_supported": currency_data.get("total_currencies", 0),
                    "total_exchange_transactions": exchange_data.get("total_transactions", 0),
                    "total_deposit_withdrawal_transactions": transaction_data.get("total_transactions", 0),
                    "total_customer_accounts": customer_data.get("total_accounts", 0),
                    "total_hawala_transactions": hawala_data.get("total_transactions", 0),
                    "total_social_posts": social_data.get("total_posts", 0),
                    "total_likes": social_data.get("total_likes", 0),
                    "total_comments": social_data.get("total_comments", 0),
                    "total_employees": employees_data.get("total_employees", 0),
                    "total_conversations": conversations_data.get("total_conversations", 0),
                    "total_messages": messages_data.get("total_messages", 0),
                    "total_customer_transactions": customer_transactions_data.get("total_transactions", 0)
                }
            }
            
            logger.info(f"Successfully collected all data for saraf_id: {saraf_id}")
            return aggregated_data
            
        except Exception as e:
            logger.error(f"Error collecting all data for saraf_id {self.saraf_id}: {str(e)}")
            return {
                "error": f"Data collection error: {str(e)}",
                "saraf_id": self.saraf_id,
                "timestamp": None
            }


def create_super_tool(authenticated_user=None):
    """
    Factory function to create SuperTool instance.
    
    Args:
        authenticated_user: CustomUser object from JWT authentication
        
    Returns:
        SuperTool instance
    """
    return SuperTool(authenticated_user)
