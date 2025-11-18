"""
Agent module with dual-tool architecture:
- SuperTool: For business data queries
- DocumentationTool: For app usage queries
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from ai.llm import get_google_model
from ai.super_tool import create_super_tool
from ai.rag_helper import RAGHelper
import json
import logging

logger = logging.getLogger(__name__)


def _build_system_prompt(authenticated_user) -> str:
    """Build system prompt for the AI agent"""
    # Extract saraf_id as integer from token
    if authenticated_user and hasattr(authenticated_user, 'saraf_id'):
        saraf_id = authenticated_user.saraf_id
        # Ensure saraf_id is an integer, not an object
        if not isinstance(saraf_id, int):
            try:
                saraf_id = int(saraf_id)
            except (ValueError, TypeError):
                saraf_id = "Unknown"
    else:
        saraf_id = "Unknown"
    
    # Extract full_name safely
    if authenticated_user and hasattr(authenticated_user, 'full_name'):
        full_name = authenticated_user.full_name
        # Ensure full_name is a string, not an object
        if not isinstance(full_name, str):
            full_name = str(full_name) if full_name else "User"
    else:
        full_name = "User"
    
    return f"""You are an AI assistant for AMU Pay Saraf (money exchanger).
Current user: {full_name} (ID: {saraf_id})

You have access to TWO specialized tools:

1. SuperTool - Use this when the user asks about their BUSINESS DATA:
   - Balances, transactions, currencies
   - Customer accounts, employees
   - Hawala transactions, messages
   - Profile information, business statistics
   - Examples: "What's my balance?", "How many customers?", "Show recent transactions"

2. DocumentationTool - Use this when the user asks about HOW TO USE THE APP:
   - App features, screens, buttons
   - How to do something in the app
   - Settings, language, theme
   - Examples: "How to change language?", "How to add currency?", "What's the welcome screen?"

IMPORTANT RULES:
- First determine if the question is about BUSINESS DATA or APP USAGE
- Use ONLY ONE tool per query - choose the most relevant one
- If question is about business data → use SuperTool
- If question is about app usage → use DocumentationTool
- If unclear, prioritize SuperTool for logged-in users asking about their account
- Answer in simple, plain text format - NO markdown, NO bold text, NO asterisks, NO special formatting
- Use simple line breaks and commas to separate information
- Use the same language as the question (Dari, Pashto, English)
- Be direct and helpful
- Format lists as simple numbered lists without markdown
- Example format: "Transaction 1: Amount 1000 AFN, Hawala Number HW123, Status: sent"
- Keep responses concise and easy to read

Current Saraf ID: {saraf_id}
"""


def get_agent(authenticated_user=None):
    """
    Create a LangChain agent with dual tools:
    - SuperTool for business data
    - DocumentationTool for app usage
    
    Args:
        authenticated_user: CustomUser object from JWT authentication
        
    Returns:
        Configured LangChain agent with both tools
    """
    try:
        # Validate authentication
        if not authenticated_user:
            raise ValueError("Authentication required to create agent")
        
        if not authenticated_user.saraf_id:
            raise ValueError("Saraf ID required in authentication token")
        
        # Extract saraf_id and ensure it's an integer
        saraf_id_raw = getattr(authenticated_user, 'saraf_id', None)
        if saraf_id_raw is None:
            raise ValueError("Saraf ID not found in authentication token")
        
        # Ensure saraf_id is an integer, not an object
        if isinstance(saraf_id_raw, int):
            saraf_id = saraf_id_raw
        elif isinstance(saraf_id_raw, str):
            try:
                saraf_id = int(saraf_id_raw)
            except ValueError:
                raise ValueError(f"Invalid saraf_id format: {saraf_id_raw}")
        else:
            raise ValueError(f"Unexpected saraf_id type: {type(saraf_id_raw)} = {saraf_id_raw}")
        
        logger.info(f"Creating agent for saraf_id: {saraf_id} (type: {type(saraf_id)})")
        
        llm = get_google_model()
        
        # ===== TOOL 1: SuperTool for Business Data =====
        super_tool_instance = create_super_tool(authenticated_user)
        
        def collect_saraf_data(query: str = "") -> str:
            """
            Collect business data for the authenticated Saraf.
            Use this when user asks about balances, transactions, customers, etc.
            
            Args:
                query: User's question (optional, for context)
                
            Returns:
                JSON string with Saraf business data
            """
            try:
                # Ensure query is a string - handle any input type from LangChain
                if query is None:
                    query = ""
                elif not isinstance(query, str):
                    # LangChain might pass dict, int, or other types
                    if isinstance(query, dict):
                        # If it's a dict, try to extract a query string
                        query = query.get('query', query.get('input', str(query)))
                    else:
                        query = str(query)
                
                logger.info(f"SuperTool called for saraf_id: {saraf_id} (type: {type(saraf_id)}), query: {query[:50] if query else 'empty'}")
                
                # Ensure saraf_id is an integer before calling collect_all_data
                if not isinstance(saraf_id, int):
                    logger.error(f"Invalid saraf_id type in collect_saraf_data: {type(saraf_id)} = {saraf_id}")
                    return json.dumps({
                        "error": f"Invalid saraf_id type: {type(saraf_id)}",
                        "saraf_id": saraf_id
                    }, ensure_ascii=False)
                
                data = super_tool_instance.collect_all_data()
                return json.dumps(data, ensure_ascii=False, indent=2)
                
            except AttributeError as e:
                # Catch attribute errors specifically (like 'int' object has no attribute 'name')
                logger.error(f"SuperTool AttributeError: {str(e)}", exc_info=True)
                return json.dumps({
                    "error": f"Attribute error: {str(e)}",
                    "saraf_id": saraf_id,
                    "saraf_id_type": str(type(saraf_id))
                }, ensure_ascii=False)
            except Exception as e:
                logger.error(f"SuperTool error: {str(e)}", exc_info=True)
                return json.dumps({
                    "error": f"Failed to collect business data: {str(e)}",
                    "saraf_id": saraf_id,
                    "saraf_id_type": str(type(saraf_id))
                }, ensure_ascii=False)
        
        super_tool = Tool(
            name="SuperTool",
            description="""Use this tool when user asks about their BUSINESS DATA:
            - Balances and currencies (e.g., "What's my USD balance?")
            - Transactions (exchange, deposit, withdrawal, hawala)
            - Customers and customer accounts
            - Employees
            - Messages and conversations
            - Profile information
            - Business statistics
            
            Input: User's question (optional)
            Output: Complete JSON with all Saraf business data
            
            Examples of when to use:
            - "What is my balance?"
            - "How many customers do I have?"
            - "Show me recent transactions"
            - "What's my phone number?"
            - "How many employees work for me?"
            """,
            func=collect_saraf_data
        )
        
        # ===== TOOL 2: DocumentationTool for App Usage =====
        
        def search_documentation(query: str) -> str:
            """
            Search app documentation for usage guidance.
            Use this when user asks HOW TO USE the app.
            
            Args:
                query: User's question about app usage
                
            Returns:
                Relevant documentation text
            """
            try:
                logger.info(f"DocumentationTool called with query: {query}")
                
                # Initialize RAG if needed
                if not RAGHelper._initialized:
                    RAGHelper.initialize()
                
                # Search documentation (now with top_k=5 as user changed)
                docs = RAGHelper.search_documentation(query, top_k=5)
                
                if not docs:
                    return "مستندات مربوط به این سوال پیدا نشد. لطفاً سوال خود را واضح‌تر بپرسید یا با تیم پشتیبانی تماس بگیرید."
                
                logger.info(f"DocumentationTool found {len(docs.split('[مستند'))-1} documents")
                return docs
                
            except Exception as e:
                logger.error(f"DocumentationTool error: {str(e)}")
                return f"خطا در جستجوی مستندات: {str(e)}"
        
        documentation_tool = Tool(
            name="DocumentationTool",
            description="""Use this tool when user asks about HOW TO USE THE APP:
            - How to do something in the app
            - What a screen/feature does
            - How to change settings (language, theme, etc.)
            - Navigation and UI elements
            - App features and functionality
            
            Input: User's question about app usage (REQUIRED)
            Output: Relevant documentation from vector database
            
            Examples of when to use:
            - "How do I change the language?" / "چطوری زبان رو عوض کنم؟"
            - "How to add a new currency?"
            - "What is the welcome screen?"
            - "How to create an employee account?"
            - "How do I change my theme?"
            
            DO NOT use this for business data queries like balances or transactions.
            """,
            func=search_documentation
        )
        
        # ===== Create Agent with Both Tools =====
        tools = [super_tool, documentation_tool]
        
        agent = create_react_agent(
            model=llm,
            tools=tools,
            state_modifier=_build_system_prompt(authenticated_user),
        )
        
        logger.info(f"✅ Agent created successfully for saraf_id: {saraf_id} with 2 tools")
        return agent
        
    except Exception as e:
        logger.error(f"❌ Error creating agent: {str(e)}")
        raise ValueError(f"Agent creation failed: {str(e)}")