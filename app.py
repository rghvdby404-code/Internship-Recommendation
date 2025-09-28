import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Internship Recommendation Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import the working scraper with jobspy
scraper_available = False
InternshipScraper = None

try:
    from scraper import InternshipScraper
    scraper_available = True
    st.success("✅ Using jobspy scraper with real job data from LinkedIn, Indeed, and Glassdoor")
except ImportError as e:
    st.error(f"❌ No scraper available. Error: {str(e)}")
    
    # Debug information
    import os
    st.error(f"Current directory: {os.getcwd()}")
    try:
        files = os.listdir('.')
        st.error(f"Files in directory: {files}")
    except:
        st.error("Could not list directory contents")
    
    # Try alternative import methods
    try:
        import scraper
        InternshipScraper = scraper.InternshipScraper
        scraper_available = True
        st.success("✅ Scraper found using alternative import method")
    except Exception as e2:
        st.error(f"❌ Alternative import also failed: {e2}")
        st.error("Please ensure scraper.py is present in the deployment.")

# Import filter after page config
from filter import InternshipFilter

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .internship-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 Internship Recommendation Engine</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for user input
    with st.sidebar:
        st.markdown('<h2 class="sub-header">📝 Your Profile</h2>', unsafe_allow_html=True)
        
        # User input fields
        name = st.text_input("👤 Your Name", placeholder="Enter your name")
        
        # Skills input
        st.markdown("**🛠️ Your Skills**")
        skills_input = st.text_area(
            "Enter your skills (comma-separated)",
            placeholder="Python, Machine Learning, Data Analysis, Web Development, React, SQL, etc.",
            height=100
        )
        
        # Location preference
        location = st.text_input("📍 Preferred Location", placeholder="e.g., Remote, New York, San Francisco")
        
        # Experience level
        experience = st.selectbox(
            "🎓 Experience Level",
            ["Beginner", "Intermediate", "Advanced", "Expert"]
        )
        
        # Stipend preference
        min_stipend = st.number_input("💰 Minimum Stipend ($)", min_value=0, value=0, step=100)
        
        # Search parameters
        st.markdown("**🔍 Search Parameters**")
        num_results = st.slider("Number of results", 10, 100, 25)
        days_old = st.slider("Maximum days old", 1, 30, 7)
        
        # Search button
        search_button = st.button("🚀 Find My Internships", type="primary", use_container_width=True)
    
    # Main content area
    if search_button:
        if not skills_input.strip():
            st.error("⚠️ Please enter your skills to get personalized recommendations!")
            return
        
        # Process skills
        skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
        
        if not skills:
            st.error("⚠️ Please enter valid skills!")
            return
        
        # Check if scraper is available
        if not scraper_available:
            st.error("❌ Scraper not available. Please check your dependencies.")
            return
        
        # Show loading
        with st.spinner("🔍 Searching for the best internships for you..."):
            try:
                # Initialize scraper and filter
                scraper = InternshipScraper()
                filter_engine = InternshipFilter()
                
                # Scrape internships
                st.info("📡 Scraping latest internship data...")
                internships = scraper.scrape_internships(
                    skills=skills,
                    location=location,
                    max_results=num_results * 2  # Get more to filter later
                )
                
                if internships.empty:
                    st.warning("😔 No internships found with your criteria. Try adjusting your search parameters.")
                    return
                
                # Filter and rank internships
                st.info("🎯 Filtering and ranking internships...")
                filtered_internships = filter_engine.filter_and_rank(
                    internships=internships,
                    user_skills=skills,
                    min_stipend=min_stipend,
                    max_days_old=days_old,
                    top_n=num_results
                )
                
                # Display results
                display_results(filtered_internships, name, skills)
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Try adjusting your search parameters or try again later.")
    
    else:
        # Welcome message
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>Welcome to the Internship Recommendation Engine! 🎉</h2>
            <p style="font-size: 1.2rem; color: #666;">
                Get personalized internship recommendations based on your skills and preferences.
            </p>
            <p style="font-size: 1rem; color: #888;">
                Fill out your profile on the left and click "Find My Internships" to get started!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🔍 Smart Scraping</h3>
                <p>Automatically finds the latest internships from multiple sources</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>🎯 Personalized Matching</h3>
                <p>Matches internships based on your skills and preferences</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Smart Ranking</h3>
                <p>Ranks opportunities by relevance, stipend, and recency</p>
            </div>
            """, unsafe_allow_html=True)

def display_results(internships, name, skills):
    """Display the filtered internship results"""
    
    if internships.empty:
        st.warning("😔 No internships match your criteria. Try adjusting your search parameters.")
        return
    
    # Header with user's name
    if name:
        st.markdown(f'<h2 class="sub-header">🎯 Recommended Internships for {name}</h2>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 class="sub-header">🎯 Your Recommended Internships</h2>', unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Found", len(internships))
    
    with col2:
        avg_stipend = internships['stipend'].mean() if 'stipend' in internships.columns else 0
        st.metric("Avg Stipend", f"${avg_stipend:.0f}")
    
    with col3:
        remote_count = len(internships[internships['location'].astype(str).str.contains('Remote', case=False, na=False)])
        st.metric("Remote Options", remote_count)
    
    with col4:
        recent_count = len(internships[internships['days_old'] <= 3])
        st.metric("Recent (≤3 days)", recent_count)
    
    st.markdown("---")
    
    # Stipend distribution chart
    if 'stipend' in internships.columns and len(internships) > 1:
        st.subheader("📊 Stipend Distribution")
        fig = px.histogram(internships, x='stipend', nbins=20, 
                          title="Distribution of Stipends",
                          labels={'stipend': 'Stipend ($)', 'count': 'Number of Internships'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Location distribution
    if 'location' in internships.columns:
        st.subheader("📍 Location Distribution")
        location_counts = internships['location'].value_counts().head(10)
        fig = px.pie(values=location_counts.values, names=location_counts.index,
                    title="Top 10 Locations")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Individual internship cards
    st.subheader("🎯 Your Personalized Recommendations")
    
    for idx, internship in internships.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="internship-card">
                <h3 style="color: #1f77b4; margin-bottom: 0.5rem;">{internship['title']}</h3>
                <p style="color: #666; margin-bottom: 0.5rem;"><strong>Company:</strong> {internship['company']}</p>
                <p style="color: #666; margin-bottom: 0.5rem;"><strong>Location:</strong> {internship['location']}</p>
                <p style="color: #666; margin-bottom: 0.5rem;"><strong>Stipend:</strong> ${internship.get('stipend', 'Not specified')}</p>
                <p style="color: #666; margin-bottom: 0.5rem;"><strong>Posted:</strong> {internship.get('days_old', 'Unknown')} days ago</p>
                <p style="color: #666; margin-bottom: 1rem;"><strong>Relevance Score:</strong> {internship.get('relevance_score', 0):.2f}/10</p>
                <p style="margin-bottom: 1rem;">{str(internship.get('description', 'No description available'))[:200]}...</p>
                <a href="{internship['apply_url']}" target="_blank" style="background-color: #28a745; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 0.25rem; display: inline-block;">Apply Now</a>
            </div>
            """, unsafe_allow_html=True)
    
    # Download option
    st.markdown("---")
    st.subheader("📥 Download Results")
    
    csv = internships.to_csv(index=False)
    st.download_button(
        label="📊 Download as CSV",
        data=csv,
        file_name=f"internship_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
