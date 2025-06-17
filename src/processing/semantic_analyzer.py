from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticAnalyzer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the SemanticAnalyzer with a specified sentence-transformer model.

        Args:
            model_name (str): The name of the sentence-transformer model to use.
        """
        try:
            self.model = SentenceTransformer(model_name)
            print(f"Model '{model_name}' loaded successfully.")
        except Exception as e:
            self.model = None
            print(f"Error loading model '{model_name}': {e}")
            print("Please ensure you have an internet connection and the model name is correct.")

    def generate_embedding(self, text: str) -> list[float] | None:
        """
        Generates a semantic embedding for the given text.

        Args:
            text (str): The input text to embed.

        Returns:
            list[float] | None: A list of floats representing the embedding,
                                or None if the model is not loaded or an error occurs.
        """
        if self.model is None:
            print("Error: Model not loaded. Cannot generate embedding.")
            return None
        if not isinstance(text, str) or not text.strip():
            print("Error: Input text must be a non-empty string.")
            return None
        try:
            embedding_np = self.model.encode(text)
            return embedding_np.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

if __name__ == '__main__':
    # Example Usage (optional - for testing)
    analyzer = SemanticAnalyzer()
    if analyzer.model:
        example_text = "This is a test sentence."
        embedding = analyzer.generate_embedding(example_text)
        if embedding:
            print(f"Embedding for '{example_text}': {embedding[:5]}... (first 5 dimensions)")
            print(f"Embedding dimension: {len(embedding)}")

        example_text_2 = "Another example for semantic analysis."
        embedding_2 = analyzer.generate_embedding(example_text_2)
        if embedding_2:
            print(f"Embedding for '{example_text_2}': {embedding_2[:5]}... (first 5 dimensions)")

        # Test empty string
        empty_text_embedding = analyzer.generate_embedding("")
        if empty_text_embedding is None:
            print("Correctly handled empty string input.")

        # Test non-string input
        non_string_embedding = analyzer.generate_embedding(123)
        if non_string_embedding is None:
            print("Correctly handled non-string input.")
    else:
        print("SemanticAnalyzer could not be initialized. Skipping example usage.")
