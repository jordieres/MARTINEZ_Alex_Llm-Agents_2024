from typing import Dict
from habanero import Crossref
from langchain.tools import Tool

def crossref(subject: str) -> Dict:
    """
    Fetches article titles and abstracts from Crossref based on a given subject.

    Args:
        subject (str): The subject of the articles to search.

    Returns:
        Dict: A dictionary containing article titles as keys and their abstracts as values. 
              If an error occurs, the dictionary contains an "error" key with the error message.
    """
    limit = 5
    results = {}
    cr = Crossref()
    try:
        result = cr.works(query=subject, limit=limit)
        for i in range(0, limit-1):
            title = result['message']['items'][i].get('title', ['No Title'])[0]
            abstract = result['message']['items'][i].get('abstract', 'No abstract available')
            results[title] = abstract
        return results
    except Exception as e:
        return {"error": str(e)}

# Create compatible tool
crossref_tool = Tool(
    name="Crossref article search",
    func=crossref,
    description="Use this tool to fetch article titles and abstracts based on a given subject."
)
