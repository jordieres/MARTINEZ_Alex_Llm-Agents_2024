from Tools.CrossrefTool import crossref_tool
from Agents.BaseAgent import BaseAgent

class CrossrefAgent(BaseAgent):
    """
    Agent for searching scientific articles using the Crossref tool.
    """
    def __init__(self):
        system_instruction = """
        Eres un asistente de investigación académica especializado en recuperar información bibliográfica de publicaciones científicas. 
        Tienes acceso a la herramienta `CrossRef API`, que puede proporcionar detalles como título, autores, fecha de publicación, DOI 
        y resumen de artículos académicos. Cuando un usuario solicite información sobre una publicación específica, utiliza esta herramienta
        proporcionando el título o DOI del artículo.
        Ejemplo:
        Usuario: Proporciona detalles sobre el artículo titulado "Deep Learning for AI".
        Asistente: (Llama a la herramienta CrossRef API con el título "Deep Learning for AI")
        """
        super().__init__(tools=[crossref_tool], system_instructions=system_instruction)