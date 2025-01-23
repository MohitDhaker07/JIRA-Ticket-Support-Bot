import os
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
    
    def generate_embeddings(self, texts):
        """
        Generate embeddings for given texts
        
        Args:
            texts (list): List of text strings to embed
        
        Returns:
            numpy.ndarray: Array of embeddings
        """
        # Batch processing for efficiency
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=batch
            )
            batch_embeddings = [embed.embedding for embed in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return np.array(all_embeddings)