import requests
from langchain.tools import Tool
from pydantic import BaseModel
from langchain.tools import StructuredTool

# Define expected input schema for the tool using Pydantic
class ArticleInput(BaseModel):
    title: str

def get_article_content(title: str) -> str:
    """
    Fetches the content of a specific article using Elsevier's APIs based on its title.

    Args:
        title (str): The title of the article to search for.

    Returns:
        str: A string containing the content or abstract of the specified article. 
             If the article cannot be found or an error occurs, an appropriate error message is returned.
    """
    API_KEY = "87ab69edd16f0cdb92e611b99b8f4ee6"
    BASE_SEARCH_URL = "https://api.elsevier.com/content/search/scopus"
    BASE_ARTICLE_URL = "https://api.elsevier.com/content/article/doi"

    # 1. Search article by title
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": API_KEY,
    }
    params = {
        "query": f"TITLE({title})",
        "count": 1,
    }
    search_response = requests.get(BASE_SEARCH_URL, headers=headers, params=params)

    if search_response.status_code != 200:
        return (f"Error: Unable to search for the article. "
                f"Status code: {search_response.status_code}, Error: {search_response.text}")

    search_data = search_response.json()
    entries = search_data.get("search-results", {}).get("entry", [])
    if not entries:
        return f"No article found with the title '{title}'."

    # 2. Fetch article identifier
    article_entry = entries[0]
    doi = article_entry.get("prism:doi")
    if not doi:
        return f"No DOI found for the article with the title '{title}'."

    # 3. Fetch article content using DOI
    article_response = requests.get(f"{BASE_ARTICLE_URL}/{doi}", headers=headers)

    if article_response.status_code != 200:
        return (f"Error: Unable to retrieve the article content. "
                f"Status code: {article_response.status_code}, Error: {article_response.text}")

    article_data = article_response.json()
    abstract = article_data.get("abstracts-retrieval-response", {}).get("coredata", {}).get("dc:description", "No abstract found")
    return f"Content of the article '{title}':\n\n{abstract}"

# Create compatible tool
elsevier_tool = StructuredTool.from_function(
    name="elsevier_article_search",
    description="Fetches article content by its title from Elsevier.",
    func=get_article_content,
    args_schema=ArticleInput,
)