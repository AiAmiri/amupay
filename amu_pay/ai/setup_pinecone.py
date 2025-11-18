"""
Script to load documentation, create embeddings, and upload to Pinecone.
Run this once to initialize the vector database with app documentation.

Usage:
    python manage.py shell < ai/setup_pinecone.py
    OR
    python ai/setup_pinecone.py
"""

import json
import os
import re
import sys
from pathlib import Path

# Add project root to path if running standalone
if __name__ == "__main__":

    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    
    # Load .env file explicitly
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    load_dotenv(dotenv_path=env_path)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amu_pay.settings')
    import django
    django.setup()

from decouple import config
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_json_documentation(path: Path) -> list[Document]:
    """Load documentation from a JSON file."""
    logger.info(f"Loading JSON documentation from: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents: list[Document] = []

    for item in data:
        if 'id' in item and 'content' in item:
            doc_id = item.get('id', 'unknown')
            title = item.get('title', 'Unknown')
            section = item.get('section', '')
            content_type = item.get('content_type', '')
            content = item.get('content', '')
            page_ref = item.get('page_ref', '')
            query_examples = item.get('query_examples', [])
            next_steps = item.get('next_steps', '')

            doc_content = f"""عنوان: {title}
بخش: {section}
نوع: {content_type}

{content}

مثال‌های سوال:
{chr(10).join(f'- {example}' for example in query_examples)}

مراحل بعدی: {next_steps}
مرجع: {page_ref}"""

            doc = Document(
                page_content=doc_content,
                metadata={
                    "doc_id": doc_id,
                    "title": title,
                    "section": section,
                    "content_type": content_type,
                    "type": "app_documentation",
                    "source": str(path)
                }
            )
            documents.append(doc)
            logger.info(f"Loaded: {title}")
        else:
            screen_name = item.get('screen_name', 'Unknown Screen')
            description = item.get('description', '')

            screen_content = f"""صفحه: {screen_name}
توضیحات: {description}

المنت‌های صفحه:
"""

            for element in item.get('elements', []):
                element_type = element.get('type', '')
                label = element.get('label', '')
                action = element.get('action', '')

                screen_content += f"\n- نوع: {element_type}\n  برچسب: {label}\n  عملکرد: {action}\n"

            doc = Document(
                page_content=screen_content,
                metadata={
                    "screen_name": screen_name,
                    "type": "app_documentation",
                    "source": str(path)
                }
            )
            documents.append(doc)
            logger.info(f"Loaded screen: {screen_name}")

    logger.info(f"Total documents loaded from JSON: {len(documents)}")
    return documents


def _load_markdown_documentation(path: Path) -> list[Document]:
    """Load documentation from a markdown or text file."""
    logger.info(f"Loading markdown documentation from: {path}")

    text = path.read_text(encoding='utf-8')
    pattern = re.compile(r'^##\s+(.*)', re.MULTILINE)
    matches = list(pattern.finditer(text))

    documents: list[Document] = []

    def _clean_body(raw: str) -> str:
        lines = [line for line in raw.splitlines() if line.strip() != '---']
        return "\n".join(lines).strip()

    if matches:
        preface = text[:matches[0].start()].strip()
        if preface:
            documents.append(
                Document(
                    page_content=_clean_body(preface),
                    metadata={
                        "doc_id": f"{path.stem}_preface",
                        "title": path.stem,
                        "type": "app_documentation",
                        "format": "markdown",
                        "source": str(path)
                    }
                )
            )

        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            title = match.group(1).strip()
            body = _clean_body(text[start:end])
            if not body:
                body = title

            page_match = re.search(r'page\s*(\d+)', title, re.IGNORECASE)
            metadata = {
                "doc_id": f"{path.stem}_{index + 1}",
                "title": title,
                "type": "app_documentation",
                "format": "markdown",
                "source": str(path)
            }
            if page_match:
                metadata["page_ref"] = f"Page {page_match.group(1)}"

            documents.append(
                Document(
                    page_content=body,
                    metadata=metadata
                )
            )
            logger.info(f"Loaded markdown section: {title}")
    else:
        stripped = _clean_body(text)
        if stripped:
            documents.append(
                Document(
                    page_content=stripped,
                    metadata={
                        "doc_id": f"{path.stem}_1",
                        "title": path.stem,
                        "type": "app_documentation",
                        "format": "markdown",
                        "source": str(path)
                    }
                )
            )
            logger.info("Loaded markdown content without section headings")

    logger.info(f"Total documents loaded from markdown: {len(documents)}")
    return documents


def load_documentation(file_path: str) -> list[Document]:
    """Load documentation from markdown/text or JSON formats."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Documentation file not found: {file_path}")

    if path.suffix.lower() == ".json":
        return _load_json_documentation(path)

    return _load_markdown_documentation(path)


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into smaller chunks for better retrieval.
    
    Args:
        documents: List of Document objects
        
    Returns:
        List of split Document objects
    """
    logger.info("Splitting documents into chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", "،", "؛", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(documents)
    logger.info(f"Total chunks created: {len(split_docs)}")
    
    return split_docs


def initialize_pinecone():
    """
    Initialize Pinecone client and create index if it doesn't exist.
    
    Returns:
        Pinecone client instance
    """
    logger.info("Initializing Pinecone...")
    
    api_key = config('PINECONE_API_KEY')
    index_name = config('PINECONE_INDEX_NAME', default='amu-pay-docs')
    
    if api_key == 'your_pinecone_api_key_here':
        raise ValueError("Please set PINECONE_API_KEY in .env file")
    
    pc = Pinecone(api_key=api_key)
    
    # Check if index exists
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        logger.info(f"Creating new index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=768,  # paraphrase-multilingual-mpnet-base-v2 dimension
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        logger.info(f"Index '{index_name}' created successfully")
    else:
        logger.info(f"Index '{index_name}' already exists")
    
    return pc


def create_embeddings():
    """
    Create HuggingFace embeddings model for multilingual support.
    
    Returns:
        HuggingFaceEmbeddings instance
    """
    logger.info("Loading embedding model...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    logger.info("Embedding model loaded successfully")
    return embeddings


def upload_to_pinecone(documents: list[Document], embeddings, pc):
    """
    Upload documents to Pinecone vector store.
    
    Args:
        documents: List of Document objects to upload
        embeddings: Embedding model instance
        pc: Pinecone client instance
    """
    logger.info("Uploading documents to Pinecone...")
    
    index_name = config('PINECONE_INDEX_NAME', default='amu-pay-docs')
    
    # Create vector store and upload
    vector_store = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        index_name=index_name
    )
    
    logger.info(f"Successfully uploaded {len(documents)} documents to Pinecone")
    return vector_store


def main():
    """Main execution function"""
    try:
        # Get documentation file path (prefer markdown extract, fallback to JSON)
        current_dir = Path(__file__).resolve().parent
        doc_candidates = [
            current_dir / "extracted_content_markdown.txt",
            current_dir / "amu_pay_documentation.md",
            current_dir / "amu_pay_documentation.json",
        ]

        doc_file = next((candidate for candidate in doc_candidates if candidate.exists()), None)

        if not doc_file:
            raise FileNotFoundError(
                "Documentation file not found. Expected one of: extracted_content_markdown.txt, "
                "amu_pay_documentation.md, amu_pay_documentation.json"
            )

        logger.info(f"Using documentation source: {doc_file}")

        # Step 1: Load documentation
        documents = load_documentation(str(doc_file))
        
        # Step 2: Split into chunks
        split_docs = split_documents(documents)
        
        # Step 3: Initialize Pinecone
        pc = initialize_pinecone()
        
        # Step 4: Create embeddings model
        embeddings = create_embeddings()
        
        # Step 5: Upload to Pinecone
        upload_to_pinecone(split_docs, embeddings, pc)
        
        logger.info("✅ Setup completed successfully!")
        logger.info(f"Total documents in Pinecone: {len(split_docs)}")
        
    except Exception as e:
        logger.error(f"❌ Error during setup: {str(e)}")
        raise


if __name__ == "__main__":
    main()
