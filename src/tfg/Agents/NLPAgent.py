from transformers import pipeline
from Agents.BaseAgent import BaseAgent

class NLPAgent(BaseAgent):
    def __init__(self, name, nlp_task='ner'):
        super().__init__(name)
        self.nlp_task = nlp_task
        self.model = pipeline(nlp_task)
    
    def perceive(self, input_text):
        self.text = input_text
    
    def act(self):
        return self.model(self.text)