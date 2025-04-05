import os
import pprint
from langchain_community.utilities import GoogleSerperAPIWrapper

def GoogleSerper():
    os.environ["SERPER_API_KEY"] = "993a5b3dfdb9975aa203ee723756b32a43a822d9"
    search = GoogleSerperAPIWrapper()