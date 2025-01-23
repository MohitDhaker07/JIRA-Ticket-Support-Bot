import pandas as pd
import numpy as np

class JIRADataProcessor:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path)
        self.preprocess_data()
    
    def preprocess_data(self):
        # Ensure date columns are datetime
        date_columns = ['Created Date', 'Resolved Date']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        # Create a combined text description for embedding
        self.df['description'] = (
            f"Ticket ID: {self.df['Ticket ID']} | " +
            f"Status: {self.df['Status']} | " +
            f"Priority: {self.df['Priority']} | " +
            f"Customer: {self.df['Customer']} | " +
            f"Summary: {self.df['Summary']} | " +
            f"Comments: {self.df['Comments']}"
        )
        
        # Clean data
        self.df['description'] = self.df['description'].fillna('')
        
        # Remove duplicate tickets
        self.df.drop_duplicates(subset=['Ticket ID'], inplace=True)
        
        return self.df
    
    def get_ticket_dataframe(self):
        return self.df