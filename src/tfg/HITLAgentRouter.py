from transformers import pipeline
from Agents import WeatherAgent, ElsevierAgent, CrossrefAgent, DBAgent

class HITLAgentRouter:
    def __init__(self, threshold=0.7):
        """
        Initialize the HITLAgentRouter with a confidence threshold for human intervention.

        Args:
        - threshold (float): Confidence threshold below which human intervention is required.
        """
        self.pipeline = pipeline("text-classification", model="distilbert-base-uncased", top_k=None)
        self.agents = {
            "weather": WeatherAgent(),
            "article content": ElsevierAgent(),
            "article title": CrossrefAgent(),
            "database": DBAgent(),
            #"generic": GenericAgent()
        }
        self.threshold = threshold

    def classify_text(self, input_text):
        """
        Classify the input text into predefined categories using a text classification model.

        Args:
        - input_text (str): The input text to classify.

        Returns:
        - Tuple[str, float]: The predicted category and its confidence score.
        """
        predictions = self.pipeline(input_text)

        # Filter predictions to include only predefined categories
        filtered_predictions = [
            pred for pred in predictions if pred['label'] in self.agents.keys()
        ]

        if not filtered_predictions:
            return "generic", 1.0  # Default to "generic" if no valid prediction

        # Select the prediction with the highest confidence score
        best_prediction = max(filtered_predictions, key=lambda x: x['score'])
        return best_prediction['label'], best_prediction['score']

    def should_intervene(self, confidence_score):
        """
        Determine if human intervention is required based on confidence score.

        Args:
        - confidence_score (float): The confidence score of the classification.

        Returns:
        - bool: True if human intervention is required, False otherwise.
        """
        return confidence_score < self.threshold

    def request_human_intervention(self, input_text: str, confidence_score: float):
        """
        Request human intervention for the given input text.

        Args:
        - input_text (str): The input text requiring human review.

        Returns:
        - str: Message indicating human intervention is required.
        """
        print(f"Low confidence ({confidence_score}) for input: '{input_text}'")
        print("Please choose a category from the following options:")
        print(", ".join(self.agents.keys()))
        selected_category = input("Enter the correct category: ")
        return selected_category.strip().lower()

    def run(self, input_text):
        """
        Route the input text to the appropriate agent or request human intervention.

        Args:
        - input_text (str): The input text to process.

        Returns:
        - str: The response from the appropriate agent or a human intervention message.
        """
        category, confidence_score = self.classify_text(input_text)

        if self.should_intervene(confidence_score):
            return self.request_human_intervention(input_text, confidence_score)

        if category in self.agents:
            agent = self.agents[category]
            return agent.run(input_text)

        return f"No agent available for category: {category}"
