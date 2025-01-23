import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

from ticket_analyzer import TicketAnalyzer
from data_processor import JIRADataProcessor

# Load environment variables
load_dotenv()

# Custom CSS for enhanced styling
def local_css():
    st.markdown("""
    <style>
    .main-container {
        background-color: #f4f4f4;
        padding: 2rem;
        border-radius: 10px;
    }
    .stApp {
        background-color: #ffffff;
    }
    .ticket-card {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
    }
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Set page configuration
    st.set_page_config(
        page_title="JIRA Ticket Analyzer",
        page_icon="🎫",
        layout="wide"
    )
    
    # Apply custom CSS
    local_css()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Title and description
    st.title("🎫 JIRA Ticket Analyzer")
    st.markdown("**Intelligent ticket search and insights powered by AI**")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload JIRA Ticket Excel", 
        type=['xlsx'], 
        help="Upload your historical JIRA ticket data"
    )
    
    # Main functionality
    if uploaded_file is not None:
        try:
            # Save and process file
            with open(os.path.join("temp", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process data
            data_processor = JIRADataProcessor(f"temp/{uploaded_file.name}")
            dataframe = data_processor.get_ticket_dataframe()
            
            # Initialize ticket analyzer
            ticket_analyzer = TicketAnalyzer(dataframe)
            
            # Advanced search with filters
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                query = st.text_input(
                    "Search Tickets", 
                    placeholder="Enter keywords, customer name, or issue description"
                )
            
            with col2:
                priority_filter = st.selectbox(
                    "Priority", 
                    ["All", "High", "Medium", "Low"]
                )
            
            with col3:
                status_filter = st.selectbox(
                    "Status", 
                    ["All", "Open", "Resolved", "Closed"]
                )
            
            # Search button
            if st.button("Analyze Tickets"):
                # Apply filters
                filtered_df = dataframe.copy()
                if priority_filter != "All":
                    filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df['Status'] == status_filter]
                
                # Find similar tickets
                similar_tickets = ticket_analyzer.find_similar_tickets(query)
                
                if not similar_tickets.empty:
                    # Ticket Results Section
                    st.markdown("## 🔍 Matching Tickets")
                    
                    for _, row in similar_tickets.iterrows():
                        with st.expander(f"Ticket #{row['Ticket ID']} - {row['Summary'][:50]}..."):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Status:** {row['Status']}")
                                st.markdown(f"**Priority:** {row['Priority']}")
                                st.markdown(f"**Customer:** {row['Customer']}")
                            
                            with col2:
                                st.markdown(f"**Created:** {row['Created Date']}")
                                st.markdown(f"**Resolved:** {row.get('Resolved Date', 'N/A')}")
                            
                            st.markdown("**Comments:**")
                            st.write(row['Comments'])
                    
                    # AI Insights
                    st.markdown("## 💡 AI Assistant Insights")
                    response = ticket_analyzer.generate_response(query, similar_tickets)
                    st.info(response)
                
                else:
                    st.warning("No matching tickets found. Try different search terms.")
        
        except Exception as e:
            st.error(f"Error processing tickets: {e}")
    
    else:
        # Welcome and guide section
        st.markdown("""
        ### How to Use
        1. 📤 Upload your JIRA ticket Excel file
        2. 🔍 Use the search bar to find tickets
        3. 🧠 Get AI-powered insights
        
        **Search Tips:**
        - Use specific keywords
        - Try different search terms
        - Filter by priority and status
        """)
    
    # Close main container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # Ensure temp directory exists
    os.makedirs("temp", exist_ok=True)
    main()