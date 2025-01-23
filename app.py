import streamlit as st
import os
from dotenv import load_dotenv

from ticket_analyzer import TicketAnalyzer
from data_processor import JIRADataProcessor

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="JIRA Ticket Analyzer",
    page_icon="🎫",
    layout="wide"
)

def main():
    st.title("🎫 JIRA Ticket Analyzer")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Upload JIRA Tickets")
        uploaded_file = st.file_uploader(
            "Choose an Excel file", 
            type=['xlsx'], 
            help="Upload your JIRA ticket history Excel file"
        )
        
        st.markdown("### Search Tips")
        st.markdown("""
        - Search by customer, status, or issue type
        - Use specific keywords from ticket summaries
        - Include context about the problem
        """)
    
    # Main content area
    if uploaded_file is not None:
        # Process uploaded file
        try:
            # Save uploaded file temporarily
            with open(os.path.join("temp", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process data
            data_processor = JIRADataProcessor(f"temp/{uploaded_file.name}")
            dataframe = data_processor.get_ticket_dataframe()
            
            # Initialize ticket analyzer
            ticket_analyzer = TicketAnalyzer(dataframe)
            
            # Query input
            query = st.text_input(
                "Enter your ticket query", 
                placeholder="Search tickets by customer, status, or issue"
            )
            
            if query:
                # Find similar tickets
                similar_tickets = ticket_analyzer.find_similar_tickets(query)
                
                # Display results
                if not similar_tickets.empty:
                    st.subheader("Similar Tickets Found")
                    
                    # Create columns for ticket details
                    cols = st.columns([1,1,1,1,1,1])
                    headers = ['Ticket ID', 'Status', 'Priority', 'Customer', 'Summary', 'Comments']
                    
                    # Display headers
                    for col, header in zip(cols, headers):
                        col.write(f"**{header}**")
                    
                    # Display ticket details
                    for _, row in similar_tickets.iterrows():
                        cols = st.columns([1,1,1,1,1,1])
                        cols[0].write(str(row['Ticket ID']))
                        cols[1].write(row['Status'])
                        cols[2].write(row['Priority'])
                        cols[3].write(row['Customer'])
                        cols[4].write(row['Summary'])
                        cols[5].write(row['Comments'])
                    
                    # Generate AI response
                    response = ticket_analyzer.generate_response(query, similar_tickets)
                    
                    # Display AI response
                    st.subheader("AI Assistant Insights")
                    st.info(response)
                else:
                    st.warning("No similar tickets found. Try a different query.")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    else:
        # Welcome message
        st.markdown("""
        ### Welcome to JIRA Ticket Analyzer
        
        📌 **How to Use:**
        1. Upload your JIRA ticket Excel file
        2. Enter a query about an issue
        3. Get insights from historical tickets
        """)

if __name__ == "__main__":
    main()