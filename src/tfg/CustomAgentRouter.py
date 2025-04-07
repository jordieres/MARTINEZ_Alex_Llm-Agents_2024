from transformers import pipeline

class CustomAgentRouter:
    def __init__(self):
        """
        Initializes the classification model using zero-shot learning.
        """
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1 )
        self.labels = ["weather", "database", "article title", "article content", "generic"]
        self.confidence_threshold = 0.7  # Adjust as needed

    def classify_text(self, text: str) -> tuple:
        """
        Uses a transformer-based model to classify the input query.
        
        Args:
            text (str): User input query.

        Returns:
            tuple: (category, confidence)
        """
        result = self.classifier(text, self.labels)
        category = result["labels"][0]  
        confidence = result["scores"][0]  

        print(f"🔍 Classified as: {category} (Confidence: {confidence:.2f})")

        return category, confidence
