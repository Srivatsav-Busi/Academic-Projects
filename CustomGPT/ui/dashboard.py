"""
Streamlit Dashboard for Srivatsav Job Search GPT
Main user interface for job search management and AI assistance.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
import yaml
from typing import Dict, List, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from knowledge_base import JobSearchKnowledgeBase
from resume_tailor import ResumeTailor, JobDescription
from recruiter_messaging import RecruiterMessaging, ContactInfo
from job_tracker import JobTracker, JobApplication, Interview
from jobs_search import JobSearchService, create_job_application_from_search
from google_drive_service import GoogleDriveService, create_google_drive_service
from word_resume_generator import create_word_resume

# Configure page
st.set_page_config(
    page_title="Srivatsav Job Search GPT",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'kb' not in st.session_state:
        st.session_state.kb = None
    if 'resume_tailor' not in st.session_state:
        st.session_state.resume_tailor = None
    if 'messaging' not in st.session_state:
        st.session_state.messaging = None
    if 'job_tracker' not in st.session_state:
        st.session_state.job_tracker = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

def load_components():
    """Load AI components."""
    try:
        if not st.session_state.initialized:
            with st.spinner("Initializing AI components..."):
                # Initialize knowledge base
                st.session_state.kb = JobSearchKnowledgeBase()
                st.session_state.kb.initialize()
                
                # Initialize resume tailor
                st.session_state.resume_tailor = ResumeTailor()
                
                # Initialize messaging
                st.session_state.messaging = RecruiterMessaging()
                
                # Initialize job tracker
                st.session_state.job_tracker = JobTracker()
                
                st.session_state.initialized = True
                st.success("AI components initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        st.session_state.initialized = False

def render_header():
    """Render the main header."""
    st.markdown('<h1 class="main-header">🚀 Srivatsav Job Search GPT Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")

def render_sidebar():
    """Render the sidebar navigation."""
    st.sidebar.title("Navigation")
    
    pages = {
        "📊 Dashboard": "dashboard",
        "🔍 Job Search": "job_search",
        "📝 Resume Tailor": "resume_tailor",
        "📄 Generated Resumes": "generated_resumes",
        "💬 Recruiter Messaging": "messaging",
        "📋 Application Tracker": "tracker",
        "🤖 AI Assistant": "ai_assistant",
        "⚙️ Settings": "settings"
    }
    
    selected_page = st.sidebar.selectbox("Select Page", list(pages.keys()))
    return pages[selected_page]

def render_dashboard():
    """Render the main dashboard."""
    st.header("📊 Job Search Dashboard")
    
    # Load components
    load_components()
    
    if not st.session_state.initialized:
        st.warning("Please initialize AI components first.")
        return
    
    # Get statistics
    stats = st.session_state.job_tracker.get_statistics()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Applications",
            value=stats.get('total_applications', 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Response Rate",
            value=f"{stats.get('response_rate', 0)}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Interviews",
            value=stats.get('total_interviews', 0),
            delta=None
        )
    
    with col4:
        active_apps = stats.get('status_counts', {}).get('applied', 0) + stats.get('status_counts', {}).get('under_review', 0)
        st.metric(
            label="Active Applications",
            value=active_apps,
            delta=None
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Applications by status
        if stats.get('status_counts'):
            status_data = pd.DataFrame(list(stats['status_counts'].items()), columns=['Status', 'Count'])
            fig = px.pie(status_data, values='Count', names='Status', title="Applications by Status")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Applications by company
        if stats.get('company_counts'):
            company_data = pd.DataFrame(list(stats['company_counts'].items()), columns=['Company', 'Count'])
            company_data = company_data.head(10)  # Top 10 companies
            fig = px.bar(company_data, x='Count', y='Company', orientation='h', title="Top Companies")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent applications
    st.subheader("Recent Applications")
    applications = st.session_state.job_tracker.get_applications(limit=10)
    
    if applications:
        df = pd.DataFrame([{
            'Company': app.company,
            'Position': app.position,
            'Status': app.status,
            'Priority': app.priority,
            'Applied': app.application_date
        } for app in applications])
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No applications found. Start by adding a new application!")

def render_job_search():
    """Render the job search page with SerpAPI integration."""
    st.header("🔍 Job Search")
    
    # Load components
    load_components()
    
    if not st.session_state.initialized:
        st.warning("Please initialize AI components first.")
        return
    
    # Check for SerpAPI key
    if not os.getenv("SERPAPI_KEY"):
        st.error("SerpAPI key not found. Please set SERPAPI_KEY environment variable.")
        st.info("Get your free API key at: https://serpapi.com/")
        return
    
    # Job search form
    with st.form("job_search_form"):
        st.subheader("Search for Jobs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title", value="ML Engineer", placeholder="e.g., Senior ML Engineer")
            location = st.text_input("Location", value="United States", placeholder="e.g., San Francisco, CA")
            limit = st.slider("Results Limit", 5, 50, 20)
        
        with col2:
            experience_level = st.selectbox("Experience Level", ["", "entry", "mid", "senior", "executive"])
            job_type = st.selectbox("Job Type", ["", "full-time", "part-time", "contract", "internship"])
            remote = st.checkbox("Include Remote Jobs", value=True)
        
        # Quick search buttons
        st.subheader("Quick Search")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("🔍 Search All Target Roles", type="primary"):
                search_all_target_roles(location, limit)
        
        with col2:
            if st.form_submit_button("🏢 Search by Company"):
                search_by_company_form()
        
        with col3:
            if st.form_submit_button("🎯 Custom Search"):
                search_custom_jobs(job_title, location, limit, experience_level, job_type, remote)
    
    # Display search results if any
    if "search_results" in st.session_state and not st.session_state.search_results.empty:
        display_search_results()

def search_all_target_roles(location: str, limit: int):
    """Search for all target roles."""
    try:
        with st.spinner("Searching for all target roles..."):
            service = JobSearchService()
            results = service.search_target_roles(location, limit // 8)  # Divide by number of roles
            
            if not results.empty:
                st.session_state.search_results = results
                st.success(f"Found {len(results)} jobs across all target roles!")
            else:
                st.warning("No jobs found for target roles.")
    except Exception as e:
        st.error(f"Error searching jobs: {e}")

def search_by_company_form():
    """Search jobs by company."""
    company = st.text_input("Company Name", placeholder="e.g., Google, Meta, Netflix")
    if company:
        try:
            with st.spinner(f"Searching jobs at {company}..."):
                service = JobSearchService()
                results = service.search_by_company(company, "United States", 20)
                
                if not results.empty:
                    st.session_state.search_results = results
                    st.success(f"Found {len(results)} jobs at {company}!")
                else:
                    st.warning(f"No jobs found at {company}.")
        except Exception as e:
            st.error(f"Error searching jobs: {e}")

def search_custom_jobs(job_title: str, location: str, limit: int, experience_level: str, job_type: str, remote: bool):
    """Search for custom job criteria."""
    try:
        with st.spinner(f"Searching for '{job_title}' in '{location}'..."):
            service = JobSearchService()
            results = service.search_jobs(
                query=job_title,
                location=location,
                limit=limit,
                experience_level=experience_level if experience_level else None,
                job_type=job_type if job_type else None,
                remote=remote
            )
            
            if not results.empty:
                st.session_state.search_results = results
                st.success(f"Found {len(results)} jobs!")
            else:
                st.warning("No jobs found matching your criteria.")
    except Exception as e:
        st.error(f"Error searching jobs: {e}")

def display_search_results():
    """Display job search results."""
    if "search_results" not in st.session_state or st.session_state.search_results.empty:
        return
    
    results = st.session_state.search_results
    
    st.subheader(f"📊 Search Results ({len(results)} jobs found)")
    
    # Display results in a table
    display_cols = ['title', 'company', 'location', 'date_posted', 'schedule_type', 'salary']
    available_cols = [col for col in display_cols if col in results.columns]
    
    # Add Google Drive link column if resumes have been generated
    if 'generated_resumes' in st.session_state and st.session_state.generated_resumes:
        # Create a mapping of job to Google Drive link
        drive_links = {}
        for resume in st.session_state.generated_resumes:
            if 'google_drive_link' in resume:
                key = f"{resume['company']}_{resume['job_title']}"
                drive_links[key] = resume['google_drive_link']
        
        # Add Google Drive links to results
        results['google_drive_link'] = results.apply(
            lambda row: drive_links.get(f"{row['company']}_{row['title']}", ""), 
            axis=1
        )
        available_cols.append('google_drive_link')
    
    st.dataframe(
        results[available_cols],
        use_container_width=True,
        height=400
    )
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Save All to Tracker", type="primary"):
            save_all_to_tracker(results)
    
    with col2:
        if st.button("📝 Generate All Resumes", type="secondary"):
            generate_all_resumes(results)
    
    with col3:
        if st.button("📋 Export to CSV"):
            export_to_csv(results)
    
    with col4:
        if st.button("🔄 New Search"):
            st.session_state.search_results = pd.DataFrame()
            st.rerun()
    
    # Individual job details
    st.subheader("📋 Job Details")
    if len(results) > 0:
        selected_idx = st.selectbox("Select a job to view details:", range(len(results)))
        if selected_idx is not None:
            job = results.iloc[selected_idx]
            display_job_details(job)

def save_all_to_tracker(results: pd.DataFrame):
    """Save all search results to job tracker."""
    try:
        tracker = st.session_state.job_tracker
        saved_count = 0
        
        for _, job in results.iterrows():
            app_data = create_job_application_from_search(job.to_dict())
            application = JobApplication(**app_data)
            tracker.add_application(application)
            saved_count += 1
        
        st.success(f"✅ Saved {saved_count} jobs to tracker!")
        st.rerun()
    except Exception as e:
        st.error(f"Error saving jobs: {e}")

def export_to_csv(results: pd.DataFrame):
    """Export search results to CSV."""
    csv = results.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"job_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def generate_all_resumes(results: pd.DataFrame):
    """Generate tailored resumes for all job search results."""
    try:
        st.subheader("📝 Generating Tailored Resumes")
        
        # Initialize resume tailor
        tailor = st.session_state.resume_tailor
        
        # Initialize Google Drive service
        drive_service = None
        if st.checkbox("☁️ Upload to Google Drive", value=True):
            drive_service = create_google_drive_service()
            if not drive_service:
                st.warning("⚠️ Google Drive not available. Resumes will be generated locally only.")
                drive_service = None
            else:
                # Use your specific Google Drive folder from config
                target_folder_id = drive_service.config.get('google_drive', {}).get('target_folder_id', '1aAPPAvPlgq5VTHbMM-QV4TRban-NZ1oF')
                folder_url = drive_service.config.get('google_drive', {}).get('folder_url', f'https://drive.google.com/drive/folders/{target_folder_id}')
                
                if drive_service.use_existing_folder(target_folder_id):
                    st.success("✅ Connected to your Google Drive folder!")
                    st.info(f"📁 **Target Folder:** [View Folder]({folder_url})")
                else:
                    st.warning("⚠️ Failed to access your Google Drive folder. Creating new folder instead.")
                    folder_id = drive_service.create_resume_folder("Generated Resumes - Srivatsav")
                    if folder_id:
                        st.success("✅ Google Drive folder created successfully!")
                    else:
                        st.warning("⚠️ Failed to create Google Drive folder. Uploading to root directory.")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        generated_resumes = []
        failed_jobs = []
        
        total_jobs = len(results)
        
        for idx, (_, job) in enumerate(results.iterrows()):
            try:
                # Update progress
                progress = (idx + 1) / total_jobs
                progress_bar.progress(progress)
                status_text.text(f"Processing {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}...")
                
                # Parse job description
                job_desc = tailor.parse_job_description(job.get('description', ''))
                
                # Generate tailored resume
                tailored_resume = tailor.tailor_resume(job_desc)
                
                # Create Word document
                word_content = create_word_resume(tailored_resume, job.get('title', ''), job.get('company', ''))
                
                # Store generated resume
                resume_data = {
                    'job_title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'resume_content': tailored_resume,
                    'word_content': word_content,
                    'job_description': job.get('description', ''),
                    'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'google_drive_link': None
                }
                
                # Upload to Google Drive if service is available
                if drive_service and word_content:
                    filename = f"Resume_{job.get('company', 'Company').replace(' ', '_')}_{job.get('title', 'Position').replace(' ', '_')}.docx"
                    upload_result = drive_service.upload_resume(
                        word_content, 
                        filename, 
                        job.get('title', ''), 
                        job.get('company', '')
                    )
                    
                    if upload_result:
                        resume_data['google_drive_link'] = upload_result['web_view_link']
                        resume_data['google_drive_file_id'] = upload_result['file_id']
                
                generated_resumes.append(resume_data)
                
            except Exception as e:
                failed_jobs.append({
                    'job_title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'error': str(e)
                })
        
        # Complete progress
        progress_bar.progress(1.0)
        status_text.text("✅ Resume generation complete!")
        
        # Display results
        if generated_resumes:
            st.success(f"✅ Successfully generated {len(generated_resumes)} tailored resumes!")
            
            # Store in session state for download
            st.session_state.generated_resumes = generated_resumes
            
            # Show Google Drive folder link if available
            if drive_service:
                folder_link = drive_service.get_folder_link()
                if folder_link:
                    st.markdown(f"📁 **Google Drive Folder:** [View All Resumes]({folder_link})")
            
            # Show preview of first resume
            if generated_resumes:
                st.subheader("📄 Preview of First Generated Resume")
                first_resume = generated_resumes[0]
                st.markdown(f"**{first_resume['job_title']} at {first_resume['company']}**")
                st.markdown(first_resume['resume_content'][:1000] + "..." if len(first_resume['resume_content']) > 1000 else first_resume['resume_content'])
            
            # Show summary
            st.subheader("📊 Generation Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Successfully Generated", len(generated_resumes))
            
            with col2:
                st.metric("Failed", len(failed_jobs))
            
            with col3:
                uploaded_count = sum(1 for r in generated_resumes if r.get('google_drive_link'))
                st.metric("Uploaded to Drive", uploaded_count)
            
            # Download options
            st.subheader("📥 Download Options")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📄 Download All Resumes (ZIP)"):
                    download_all_resumes_zip(generated_resumes)
            
            with col2:
                if st.button("📋 Download Summary (CSV)"):
                    download_resume_summary(generated_resumes)
            
            with col3:
                if st.button("💾 Save to Tracker with Resumes"):
                    save_jobs_with_resumes(results, generated_resumes)
            
            with col4:
                if st.button("🔄 Refresh Page"):
                    st.rerun()
        
        if failed_jobs:
            st.warning(f"⚠️ Failed to generate resumes for {len(failed_jobs)} jobs:")
            for failed in failed_jobs[:5]:  # Show first 5 failures
                st.text(f"• {failed['job_title']} at {failed['company']}: {failed['error']}")
        
    except Exception as e:
        st.error(f"Error generating resumes: {e}")

def download_all_resumes_zip(generated_resumes: List[Dict]):
    """Download all generated resumes as a ZIP file."""
    import zipfile
    import io
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, resume_data in enumerate(generated_resumes):
            # Create filename
            company = resume_data['company'].replace(' ', '_').replace('/', '_')
            title = resume_data['job_title'].replace(' ', '_').replace('/', '_')
            
            # Add Markdown resume
            md_filename = f"resume_{company}_{title}_{i+1}.md"
            zip_file.writestr(md_filename, resume_data['resume_content'])
            
            # Add Word document if available
            if resume_data.get('word_content'):
                docx_filename = f"resume_{company}_{title}_{i+1}.docx"
                zip_file.writestr(docx_filename, resume_data['word_content'])
    
    zip_buffer.seek(0)
    
    # Download ZIP file
    st.download_button(
        label="📥 Download ZIP File",
        data=zip_buffer.getvalue(),
        file_name=f"tailored_resumes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
        mime="application/zip"
    )

def download_resume_summary(generated_resumes: List[Dict]):
    """Download a summary CSV of generated resumes."""
    summary_data = []
    for resume in generated_resumes:
        summary_data.append({
            'Job Title': resume['job_title'],
            'Company': resume['company'],
            'Location': resume['location'],
            'Generated At': resume['generated_at'],
            'Resume Length': len(resume['resume_content']),
            'Google Drive Link': resume.get('google_drive_link', 'Not uploaded'),
            'Word Document': 'Yes' if resume.get('word_content') else 'No'
        })
    
    df = pd.DataFrame(summary_data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Summary CSV",
        data=csv,
        file_name=f"resume_generation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def save_jobs_with_resumes(results: pd.DataFrame, generated_resumes: List[Dict]):
    """Save jobs to tracker along with their generated resumes."""
    try:
        tracker = st.session_state.job_tracker
        saved_count = 0
        
        # Create a mapping of job to resume
        resume_map = {}
        for resume in generated_resumes:
            key = f"{resume['company']}_{resume['job_title']}"
            resume_map[key] = resume
        
        for _, job in results.iterrows():
            # Create job application
            app_data = create_job_application_from_search(job.to_dict())
            application = JobApplication(**app_data)
            
            # Add generated resume if available
            key = f"{job.get('company', '')}_{job.get('title', '')}"
            if key in resume_map:
                application.notes = f"Generated tailored resume on {datetime.now().strftime('%Y-%m-%d')}"
                application.job_description = resume_map[key]['resume_content']
            
            tracker.add_application(application)
            saved_count += 1
        
        st.success(f"✅ Saved {saved_count} jobs with tailored resumes to tracker!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error saving jobs with resumes: {e}")

def display_job_details(job: pd.Series):
    """Display detailed information about a selected job."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Title:** {job.get('title', 'N/A')}")
        st.markdown(f"**Company:** {job.get('company', 'N/A')}")
        st.markdown(f"**Location:** {job.get('location', 'N/A')}")
        st.markdown(f"**Posted:** {job.get('date_posted', 'N/A')}")
        st.markdown(f"**Schedule:** {job.get('schedule_type', 'N/A')}")
        st.markdown(f"**Salary:** {job.get('salary', 'N/A')}")
        
        if job.get('description'):
            st.markdown("**Description:**")
            st.text(job.get('description', '')[:500] + "..." if len(job.get('description', '')) > 500 else job.get('description', ''))
    
    with col2:
        if job.get('link'):
            st.markdown(f"[🔗 Apply Here]({job.get('link')})")
        
        if st.button("💾 Save This Job", type="primary"):
            try:
                app_data = create_job_application_from_search(job.to_dict())
                application = JobApplication(**app_data)
                app_id = st.session_state.job_tracker.add_application(application)
                st.success(f"✅ Saved job (ID: {app_id})")
            except Exception as e:
                st.error(f"Error saving job: {e}")
        
        # Generate resume for this specific job
        if st.button("📝 Generate Resume", type="secondary"):
            generate_single_resume(job)

def generate_single_resume(job: pd.Series):
    """Generate a tailored resume for a single job."""
    try:
        with st.spinner("Generating tailored resume..."):
            tailor = st.session_state.resume_tailor
            
            # Parse job description
            job_desc = tailor.parse_job_description(job.get('description', ''))
            
            # Generate tailored resume
            tailored_resume = tailor.tailor_resume(job_desc)
            
            # Display the resume
            st.subheader(f"📝 Tailored Resume for {job.get('title', '')} at {job.get('company', '')}")
            st.markdown(tailored_resume)
            
            # Download option
            st.download_button(
                label="📥 Download Resume",
                data=tailored_resume,
                file_name=f"resume_{job.get('company', 'company').replace(' ', '_')}_{job.get('title', 'position').replace(' ', '_')}.md",
                mime="text/markdown"
            )
            
    except Exception as e:
        st.error(f"Error generating resume: {e}")

def render_generated_resumes():
    """Render the generated resumes page."""
    st.header("📄 Generated Resumes")
    
    # Check if there are any generated resumes
    if "generated_resumes" not in st.session_state or not st.session_state.generated_resumes:
        st.info("No resumes have been generated yet. Go to the Job Search page and click 'Generate All Resumes' to create tailored resumes for job postings.")
        return
    
    resumes = st.session_state.generated_resumes
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Generated", len(resumes))
    
    with col2:
        unique_companies = len(set(resume['company'] for resume in resumes))
        st.metric("Unique Companies", unique_companies)
    
    with col3:
        total_length = sum(len(resume['resume_content']) for resume in resumes)
        avg_length = total_length // len(resumes) if resumes else 0
        st.metric("Avg Resume Length", f"{avg_length:,} chars")
    
    with col4:
        latest_generation = max(resume['generated_at'] for resume in resumes) if resumes else "N/A"
        st.metric("Last Generated", latest_generation.split()[0] if latest_generation != "N/A" else "N/A")
    
    st.markdown("---")
    
    # Filter and search options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search resumes by company or job title:", placeholder="e.g., Google, Senior ML Engineer")
    
    with col2:
        sort_by = st.selectbox("Sort by:", ["Generated At (Newest)", "Generated At (Oldest)", "Company A-Z", "Company Z-A", "Job Title A-Z"])
    
    # Filter resumes based on search
    filtered_resumes = resumes
    if search_term:
        filtered_resumes = [
            resume for resume in resumes 
            if search_term.lower() in resume['company'].lower() or 
               search_term.lower() in resume['job_title'].lower()
        ]
    
    # Sort resumes
    if sort_by == "Generated At (Newest)":
        filtered_resumes.sort(key=lambda x: x['generated_at'], reverse=True)
    elif sort_by == "Generated At (Oldest)":
        filtered_resumes.sort(key=lambda x: x['generated_at'])
    elif sort_by == "Company A-Z":
        filtered_resumes.sort(key=lambda x: x['company'])
    elif sort_by == "Company Z-A":
        filtered_resumes.sort(key=lambda x: x['company'], reverse=True)
    elif sort_by == "Job Title A-Z":
        filtered_resumes.sort(key=lambda x: x['job_title'])
    
    # Display resumes
    if not filtered_resumes:
        st.warning("No resumes match your search criteria.")
        return
    
    st.subheader(f"📋 Found {len(filtered_resumes)} resume(s)")
    
    # Resume selection
    resume_options = [f"{resume['job_title']} at {resume['company']} ({resume['location']})" for resume in filtered_resumes]
    selected_idx = st.selectbox("Select a resume to view:", range(len(filtered_resumes)), format_func=lambda x: resume_options[x])
    
    if selected_idx is not None:
        selected_resume = filtered_resumes[selected_idx]
        
        # Resume details
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"📝 {selected_resume['job_title']}")
            st.markdown(f"**Company:** {selected_resume['company']}")
            st.markdown(f"**Location:** {selected_resume['location']}")
            st.markdown(f"**Generated:** {selected_resume['generated_at']}")
        
        with col2:
            # Download individual resume
            st.download_button(
                label="📥 Download Resume",
                data=selected_resume['resume_content'],
                file_name=f"resume_{selected_resume['company'].replace(' ', '_')}_{selected_resume['job_title'].replace(' ', '_')}.md",
                mime="text/markdown"
            )
            
            # View original job description
            if st.button("👁️ View Original Job"):
                st.session_state.show_job_description = selected_resume
        
        # Display resume content
        st.markdown("---")
        st.markdown("### Resume Content")
        st.markdown(selected_resume['resume_content'])
        
        # Show original job description if requested
        if st.session_state.get('show_job_description') == selected_resume:
            st.markdown("---")
            st.markdown("### Original Job Description")
            st.text(selected_resume['job_description'])
    
    # Bulk actions
    st.markdown("---")
    st.subheader("📥 Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download All Resumes (ZIP)"):
            download_all_resumes_zip(filtered_resumes)
    
    with col2:
        if st.button("📋 Download Summary (CSV)"):
            download_resume_summary(filtered_resumes)
    
    with col3:
        if st.button("🗑️ Clear All Resumes"):
            st.session_state.generated_resumes = []
            st.rerun()

def render_resume_tailor():
    """Render the resume tailoring page."""
    st.header("📝 Resume Tailor")
    
    # Load components
    load_components()
    
    if not st.session_state.initialized:
        st.warning("Please initialize AI components first.")
        return
    
    # Resume tailoring form
    with st.form("resume_tailor_form"):
        st.subheader("Tailor Your Resume")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company = st.text_input("Company", placeholder="e.g., Google")
            position = st.text_input("Position", placeholder="e.g., Senior Data Engineer")
            location = st.text_input("Location", placeholder="e.g., Mountain View, CA")
        
        with col2:
            experience_level = st.selectbox("Experience Level", ["Entry", "Mid", "Senior", "Staff", "Principal"])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        job_description = st.text_area("Job Description", placeholder="Paste the complete job description here...")
        
        submitted = st.form_submit_button("Tailor Resume")
        
        if submitted and job_description:
            with st.spinner("Tailoring resume..."):
                try:
                    # Parse job description
                    job_desc = st.session_state.resume_tailor.parse_job_description(job_description)
                    job_desc.company = company
                    job_desc.title = position
                    job_desc.location = location
                    
                    # Generate tailored resume
                    tailored_resume = st.session_state.resume_tailor.tailor_resume(job_desc)
                    
                    # Display results
                    st.subheader("Tailored Resume")
                    st.markdown(tailored_resume)
                    
                    # Generate cover letter
                    st.subheader("Cover Letter")
                    cover_letter = st.session_state.resume_tailor.generate_cover_letter(job_desc)
                    st.markdown(cover_letter)
                    
                    # Get suggestions
                    st.subheader("Tailoring Suggestions")
                    suggestions = st.session_state.resume_tailor.get_tailoring_suggestions(job_desc)
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
                    
                except Exception as e:
                    st.error(f"Error tailoring resume: {e}")

def render_messaging():
    """Render the recruiter messaging page."""
    st.header("💬 Recruiter Messaging")
    
    # Load components
    load_components()
    
    if not st.session_state.initialized:
        st.warning("Please initialize AI components first.")
        return
    
    # Messaging form
    with st.form("messaging_form"):
        st.subheader("Generate Messages")
        
        col1, col2 = st.columns(2)
        
        with col1:
            contact_name = st.text_input("Contact Name", placeholder="e.g., Sarah Johnson")
            company = st.text_input("Company", placeholder="e.g., Google")
            role = st.text_input("Role", placeholder="e.g., Senior Recruiter")
            location = st.text_input("Location", placeholder="e.g., Mountain View, CA")
        
        with col2:
            connection_type = st.selectbox("Connection Type", ["recruiter", "hiring_manager", "employee", "alumni"])
            mutual_connections = st.number_input("Mutual Connections", min_value=0, value=0)
            shared_experience = st.text_input("Shared Experience", placeholder="e.g., Data Engineering")
        
        target_job = st.text_input("Target Job", placeholder="e.g., Senior Data Engineer")
        message_type = st.selectbox("Message Type", ["connection_request", "follow_up", "networking", "thank_you"])
        
        submitted = st.form_submit_button("Generate Message")
        
        if submitted and contact_name and company:
            with st.spinner("Generating message..."):
                try:
                    # Create contact info
                    contact = ContactInfo(
                        name=contact_name,
                        company=company,
                        role=role,
                        location=location,
                        connection_type=connection_type,
                        mutual_connections=mutual_connections,
                        shared_experience=shared_experience
                    )
                    
                    # Generate message based on type
                    if message_type == "connection_request":
                        message = st.session_state.messaging.generate_linkedin_connection_request(contact, target_job)
                        st.subheader("LinkedIn Connection Request")
                    elif message_type == "follow_up":
                        message = st.session_state.messaging.generate_follow_up_message(contact, target_job, 7)
                        st.subheader("Follow-up Message")
                    elif message_type == "networking":
                        message = st.session_state.messaging.generate_networking_message(contact, "Data Engineering Summit 2023")
                        st.subheader("Networking Message")
                    else:
                        message = st.session_state.messaging.generate_recruiter_email(contact, target_job)
                        st.subheader("Recruiter Email")
                    
                    st.text_area("Generated Message", value=message, height=200)
                    
                except Exception as e:
                    st.error(f"Error generating message: {e}")

def render_tracker():
    """Render the application tracker page."""
    st.header("📋 Application Tracker")
    
    # Load components
    load_components()
    
    if not st.session_state.initialized:
        st.warning("Please initialize AI components first.")
        return
    
    # Application management
    tab1, tab2, tab3 = st.tabs(["View Applications", "Add Application", "Add Interview"])
    
    with tab1:
        st.subheader("All Applications")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "applied", "under_review", "interview_scheduled", "rejected", "offer_received"])
        
        with col2:
            company_filter = st.text_input("Filter by Company", placeholder="e.g., Google")
        
        with col3:
            priority_filter = st.selectbox("Filter by Priority", ["All", "high", "medium", "low"])
        
        # Get applications
        applications = st.session_state.job_tracker.get_applications()
        
        # Apply filters
        if status_filter != "All":
            applications = [app for app in applications if app.status == status_filter]
        
        if company_filter:
            applications = [app for app in applications if company_filter.lower() in app.company.lower()]
        
        if priority_filter != "All":
            applications = [app for app in applications if app.priority == priority_filter]
        
        # Display applications
        if applications:
            for app in applications:
                with st.expander(f"{app.company} - {app.position} ({app.status})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Location:** {app.location}")
                        st.write(f"**Priority:** {app.priority}")
                        st.write(f"**Applied:** {app.application_date}")
                        st.write(f"**Recruiter:** {app.recruiter_name}")
                    
                    with col2:
                        st.write(f"**Status:** {app.status}")
                        st.write(f"**Follow-up:** {app.follow_up_date}")
                        st.write(f"**Interview:** {app.interview_date}")
                        st.write(f"**Notes:** {app.notes}")
                    
                    if app.job_url:
                        st.write(f"**Job URL:** {app.job_url}")
                    
                    if app.job_description:
                        st.write("**Job Description:**")
                        st.text(app.job_description[:500] + "..." if len(app.job_description) > 500 else app.job_description)
        else:
            st.info("No applications found.")
    
    with tab2:
        st.subheader("Add New Application")
        
        with st.form("add_application_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company *", placeholder="e.g., Google")
                position = st.text_input("Position *", placeholder="e.g., Senior Data Engineer")
                location = st.text_input("Location", placeholder="e.g., Mountain View, CA")
                job_url = st.text_input("Job URL", placeholder="https://...")
            
            with col2:
                status = st.selectbox("Status", ["applied", "under_review", "interview_scheduled", "rejected", "offer_received"])
                priority = st.selectbox("Priority", ["high", "medium", "low"])
                salary_range = st.text_input("Salary Range", placeholder="e.g., $180K-$220K")
                recruiter_name = st.text_input("Recruiter Name", placeholder="e.g., Sarah Johnson")
            
            job_description = st.text_area("Job Description", placeholder="Paste the job description here...")
            notes = st.text_area("Notes", placeholder="Additional notes...")
            
            submitted = st.form_submit_button("Add Application")
            
            if submitted and company and position:
                application = JobApplication(
                    company=company,
                    position=position,
                    location=location,
                    job_url=job_url,
                    job_description=job_description,
                    application_date=datetime.now().strftime("%Y-%m-%d"),
                    status=status,
                    priority=priority,
                    salary_range=salary_range,
                    recruiter_name=recruiter_name,
                    notes=notes
                )
                
                app_id = st.session_state.job_tracker.add_application(application)
                st.success(f"Added application for {position} at {company} (ID: {app_id})")
    
    with tab3:
        st.subheader("Add Interview")
        
        # Get applications for selection
        applications = st.session_state.job_tracker.get_applications()
        if not applications:
            st.warning("No applications found. Add an application first.")
        else:
            with st.form("add_interview_form"):
                # Select application
                app_options = {f"{app.company} - {app.position}": app.id for app in applications}
                selected_app = st.selectbox("Select Application", list(app_options.keys()))
                application_id = app_options[selected_app]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    interview_date = st.date_input("Interview Date")
                    interview_type = st.selectbox("Interview Type", ["phone", "video", "onsite"])
                    interviewer_name = st.text_input("Interviewer Name", placeholder="e.g., John Smith")
                
                with col2:
                    interviewer_title = st.text_input("Interviewer Title", placeholder="e.g., Hiring Manager")
                    next_steps = st.text_input("Next Steps", placeholder="e.g., Technical interview next week")
                
                questions_asked = st.text_area("Questions Asked", placeholder="List the questions that were asked...")
                my_answers = st.text_area("My Answers", placeholder="Record your answers...")
                feedback_received = st.text_area("Feedback Received", placeholder="Any feedback from the interviewer...")
                preparation_notes = st.text_area("Preparation Notes", placeholder="Notes for preparation...")
                
                submitted = st.form_submit_button("Add Interview")
                
                if submitted:
                    interview = Interview(
                        application_id=application_id,
                        interview_date=interview_date.strftime("%Y-%m-%d"),
                        interview_type=interview_type,
                        interviewer_name=interviewer_name,
                        interviewer_title=interviewer_title,
                        questions_asked=questions_asked,
                        my_answers=my_answers,
                        feedback_received=feedback_received,
                        next_steps=next_steps,
                        preparation_notes=preparation_notes
                    )
                    
                    interview_id = st.session_state.job_tracker.add_interview(interview)
                    st.success(f"Added interview (ID: {interview_id})")

def render_ai_assistant():
    """Render the AI assistant page."""
    st.header("🤖 AI Assistant")
    
    # Load components
    load_components()
    
    if not st.session_state.initialized:
        st.warning("Please initialize AI components first.")
        return
    
    # Chat interface
    st.subheader("Chat with Your AI Job Search Advisor")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your job search..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.kb.query(prompt)
                    st.markdown(response["answer"])
                    
                    # Add AI response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
                    
                except Exception as e:
                    st.error(f"Error generating response: {e}")

def render_settings():
    """Render the settings page."""
    st.header("⚙️ Settings")
    
    # Configuration display
    st.subheader("Current Configuration")
    
    try:
        with open("config/settings.yaml", "r") as file:
            config = yaml.safe_load(file)
        
        st.json(config)
        
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
    
    # Environment variables
    st.subheader("Environment Variables")
    
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["SERPAPI_KEY", "INDEED_API_KEY", "GLASSDOOR_API_KEY"]
    
    st.write("**Required:**")
    for var in required_vars:
        value = os.getenv(var, "Not set")
        if value == "Not set":
            st.error(f"{var}: {value}")
        else:
            st.success(f"{var}: {'*' * 20}")
    
    st.write("**Optional:**")
    for var in optional_vars:
        value = os.getenv(var, "Not set")
        if value == "Not set":
            st.warning(f"{var}: {value}")
        else:
            st.success(f"{var}: {'*' * 20}")

def main():
    """Main function to run the Streamlit app."""
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Render selected page
    if selected_page == "dashboard":
        render_dashboard()
    elif selected_page == "job_search":
        render_job_search()
    elif selected_page == "resume_tailor":
        render_resume_tailor()
    elif selected_page == "generated_resumes":
        render_generated_resumes()
    elif selected_page == "messaging":
        render_messaging()
    elif selected_page == "tracker":
        render_tracker()
    elif selected_page == "ai_assistant":
        render_ai_assistant()
    elif selected_page == "settings":
        render_settings()

if __name__ == "__main__":
    main()
