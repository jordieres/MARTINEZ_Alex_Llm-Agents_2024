from typing import Dict
from habanero import Crossref
from pydantic import BaseModel
from langchain.tools import StructuredTool

# Define input schema
class CrossrefInput(BaseModel):
    subject: str

# Update function to return str instead of dict for clarity with LLMs
def crossref(subject: str) -> str:
    """
    Fetches article titles and abstracts from Crossref based on a given subject.

    Args:
        subject (str): The subject of the articles to search.

    Returns:
        str: A formatted string containing article titles and abstracts.
    """
    limit = 10
    cr = Crossref()
    try:
        result = cr.works(query=subject, limit=limit)
        output = []
        for i in range(0, limit - 1):
            title = result['message']['items'][i].get('title', ['No Title'])[0]
            abstract = result['message']['items'][i].get('abstract', 'No abstract available')
            output.append(f"🔹 Title: {title}\n📝 Abstract: {abstract}")
        return "\n\n".join(output)
    except Exception as e:
        return f"❌ Error fetching articles: {str(e)}"

# Structured tool
crossref_tool = StructuredTool.from_function(
    name="crossref_article_search",
    func=crossref,
    description="Fetch article titles and abstracts from Crossref based on a subject.",
    args_schema=CrossrefInput,
)