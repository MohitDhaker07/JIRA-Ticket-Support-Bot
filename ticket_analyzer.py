import os
import numpy as np
from openai import OpenAI
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

from    embedding_service import EmbeddingService

load_dotenv()

class TicketAnalyzer:
    def __init__(self, dataframe):
        self.df = dataframe
        self.embedding_service = EmbeddingService()
        self.client = OpenAI()
        self.chat_model = os.getenv('CHAT_MODEL', 'gpt-3.5-turbo')
        
        # Precompute embeddings with more comprehensive text
        self.df['full_text'] = self.df.apply(
            lambda row: f"Ticket ID: {row['Ticket ID']} "
                        f"Status: {row['Status']} "
                        f"Priority: {row['Priority']} "
                        f"Customer: {row['Customer']} "
                        f"Summary: {row['Summary']} "
                        f"Comments: {row['Comments']}", 
            axis=1
        )
        
        # Generate embeddings
        self.embeddings = self.embedding_service.generate_embeddings(
            self.df['full_text'].tolist()
        )
    
    def find_similar_tickets(self, query, top_k=5, similarity_threshold=0.5):
        """
        Find similar tickets with more flexible matching
        """
        # Enhance query with synonyms and variations
        enhanced_query = self._enhance_query(query)
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embeddings([enhanced_query])[0]
        
        # Calculate cosine similarities
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Sort and filter similar tickets
        similar_indices = similarities.argsort()[-top_k:][::-1]
        
        # Collect tickets above threshold or top matches
        filtered_tickets = []
        for idx in similar_indices:
            if similarities[idx] >= similarity_threshold:
                filtered_tickets.append(self.df.iloc[idx])
        
        # If no tickets meet threshold, return top matches
        if not filtered_tickets:
            filtered_tickets = [self.df.iloc[similar_indices[0]]]
        
        return pd.DataFrame(filtered_tickets)
    
    def _enhance_query(self, query):
        """
        Enhance query with synonyms and context
        """
        synonyms = {
            'bug': ['issue', 'problem', 'error'],
            'ui': ['interface', 'layout', 'design'],
            'login': ['authentication', 'signin', 'access'],
            'performance': ['speed', 'slow', 'timeout']
        }
        
        # Add synonyms to query
        for key, syn_list in synonyms.items():
            if key in query.lower():
                query += ' ' + ' '.join(syn_list)
        
        return query
    
    def generate_response(self, query, similar_tickets):
        """
        Generate AI-powered response with fallback
        """
        if similar_tickets.empty:
            return "No similar tickets found. The query might be too specific."
        
        # Prepare context for AI
        context = similar_tickets[['Ticket ID', 'Status', 'Priority', 'Summary', 'Comments']].to_string(index=False)
        
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful JIRA ticket assistant. Analyze the ticket history and provide insights."
                    },
                    {
                        "role": "user", 
                        "content": f"Query: {query}\n\nRelevant Ticket History:\n{context}\n\nPlease provide a comprehensive analysis or solution based on these tickets."
                    }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response: {str(e)}. Similar tickets found but AI analysis failed."