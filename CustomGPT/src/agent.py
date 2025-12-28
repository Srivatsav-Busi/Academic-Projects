"""
Autonomous Job Search Agent for Srivatsav Job Search GPT
Implements agentic capabilities for automated job search and application workflow.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from knowledge_base import JobSearchKnowledgeBase
from resume_tailor import ResumeTailor, JobDescription
from recruiter_messaging import RecruiterMessaging, ContactInfo
from job_tracker import JobTracker, JobApplication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """Data class for agent state information."""
    current_task: str = ""
    active_applications: List[int] = None
    pending_follow_ups: List[int] = None
    daily_application_count: int = 0
    last_activity: str = ""
    status: str = "idle"  # idle, searching, applying, following_up

@dataclass
class SearchCriteria:
    """Data class for job search criteria."""
    keywords: List[str]
    companies: List[str]
    locations: List[str]
    experience_level: str
    job_types: List[str]
    salary_range: Tuple[int, int]
    remote_ok: bool = True

class JobSearchAgent:
    """
    Autonomous job search agent that can search, apply, and follow up on jobs.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the job search agent."""
        self.config = self._load_config(config_path)
        self.state = AgentState()
        
        # Initialize components
        self.kb = JobSearchKnowledgeBase(config_path)
        self.resume_tailor = ResumeTailor(config_path)
        self.messaging = RecruiterMessaging(config_path)
        self.job_tracker = JobTracker()
        
        # Initialize agent
        self.kb.initialize()
        
        # Load search criteria
        self.search_criteria = self._load_search_criteria()
        
        logger.info("Job Search Agent initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _load_search_criteria(self) -> SearchCriteria:
        """Load search criteria from configuration."""
        target_roles = self.config.get("target_roles", {}).get("primary", [])
        target_companies = self.config.get("target_companies", {}).get("tier_1", [])
        locations = self.config.get("locations", {}).get("primary", [])
        salary = self.config.get("salary", {})
        
        return SearchCriteria(
            keywords=target_roles,
            companies=target_companies,
            locations=locations,
            experience_level="senior",
            job_types=["full-time"],
            salary_range=(salary.get("minimum", 180000), salary.get("maximum", 280000)),
            remote_ok=True
        )
    
    async def run_daily_workflow(self) -> Dict[str, Any]:
        """
        Run the daily autonomous workflow.
        
        Returns:
            Dictionary with workflow results
        """
        logger.info("Starting daily workflow...")
        self.state.status = "searching"
        self.state.last_activity = datetime.now().isoformat()
        
        results = {
            "applications_processed": 0,
            "follow_ups_sent": 0,
            "new_jobs_found": 0,
            "errors": []
        }
        
        try:
            # 1. Check for follow-ups
            await self._process_follow_ups(results)
            
            # 2. Search for new jobs
            await self._search_new_jobs(results)
            
            # 3. Process new applications
            await self._process_new_applications(results)
            
            # 4. Update application statuses
            await self._update_application_statuses(results)
            
            self.state.status = "idle"
            logger.info("Daily workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily workflow: {e}")
            results["errors"].append(str(e))
            self.state.status = "idle"
        
        return results
    
    async def _process_follow_ups(self, results: Dict[str, Any]) -> None:
        """Process pending follow-ups."""
        logger.info("Processing follow-ups...")
        
        try:
            # Get applications needing follow-up
            follow_up_apps = self.job_tracker.get_follow_up_reminders()
            
            for app in follow_up_apps:
                try:
                    # Generate follow-up message
                    contact = ContactInfo(
                        name=app.recruiter_name or "Hiring Manager",
                        company=app.company,
                        role="Recruiter",
                        location=app.location,
                        connection_type="recruiter",
                        mutual_connections=0,
                        shared_experience="Data Engineering"
                    )
                    
                    message = self.messaging.generate_follow_up_message(
                        contact, app.position, 7
                    )
                    
                    # Update follow-up date
                    next_follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    self.job_tracker.update_application(app.id, {
                        "follow_up_date": next_follow_up,
                        "notes": f"Follow-up sent: {message[:100]}..."
                    })
                    
                    results["follow_ups_sent"] += 1
                    logger.info(f"Generated follow-up for {app.company} - {app.position}")
                    
                except Exception as e:
                    logger.error(f"Error processing follow-up for {app.company}: {e}")
                    results["errors"].append(f"Follow-up error for {app.company}: {e}")
        
        except Exception as e:
            logger.error(f"Error processing follow-ups: {e}")
            results["errors"].append(f"Follow-up processing error: {e}")
    
    async def _search_new_jobs(self, results: Dict[str, Any]) -> None:
        """Search for new job opportunities."""
        logger.info("Searching for new jobs...")
        
        try:
            # This would integrate with job search APIs
            # For now, we'll simulate job discovery
            new_jobs = await self._discover_jobs()
            
            for job in new_jobs:
                try:
                    # Check if already applied
                    existing_apps = self.job_tracker.get_applications(company=job["company"])
                    if any(app.position == job["position"] for app in existing_apps):
                        continue
                    
                    # Create job application
                    application = JobApplication(
                        company=job["company"],
                        position=job["position"],
                        location=job["location"],
                        job_url=job["url"],
                        job_description=job["description"],
                        application_date=datetime.now().strftime("%Y-%m-%d"),
                        status="discovered",
                        priority=self._calculate_priority(job),
                        notes="Discovered by AI agent"
                    )
                    
                    # Add to tracker
                    app_id = self.job_tracker.add_application(application)
                    results["new_jobs_found"] += 1
                    logger.info(f"Discovered new job: {job['position']} at {job['company']}")
                    
                except Exception as e:
                    logger.error(f"Error processing job {job.get('company', 'Unknown')}: {e}")
                    results["errors"].append(f"Job processing error: {e}")
        
        except Exception as e:
            logger.error(f"Error searching for jobs: {e}")
            results["errors"].append(f"Job search error: {e}")
    
    async def _discover_jobs(self) -> List[Dict[str, Any]]:
        """Discover new job opportunities (simulated)."""
        # This would integrate with real job search APIs
        # For now, return simulated data
        return [
            {
                "company": "Google",
                "position": "Senior Data Engineer",
                "location": "Mountain View, CA",
                "url": "https://careers.google.com/jobs/results/123456",
                "description": "Looking for a Senior Data Engineer with GCP experience...",
                "priority": "high"
            },
            {
                "company": "Meta",
                "position": "ML Engineer",
                "location": "Menlo Park, CA",
                "url": "https://careers.meta.com/jobs/123456",
                "description": "Seeking an ML Engineer for real-time ML systems...",
                "priority": "high"
            }
        ]
    
    def _calculate_priority(self, job: Dict[str, Any]) -> str:
        """Calculate priority for a job based on criteria."""
        company = job.get("company", "").lower()
        position = job.get("position", "").lower()
        
        # High priority for tier 1 companies
        tier_1_companies = [c.lower() for c in self.search_criteria.companies]
        if company in tier_1_companies:
            return "high"
        
        # High priority for senior roles
        if "senior" in position or "staff" in position or "principal" in position:
            return "high"
        
        return "medium"
    
    async def _process_new_applications(self, results: Dict[str, Any]) -> None:
        """Process new applications that need attention."""
        logger.info("Processing new applications...")
        
        try:
            # Get applications that need processing
            new_apps = self.job_tracker.get_applications(status="discovered")
            
            for app in new_apps:
                try:
                    # Check daily application limit
                    if self.state.daily_application_count >= self.config.get("application", {}).get("daily_limit", 5):
                        logger.info("Daily application limit reached")
                        break
                    
                    # Process application
                    await self._process_application(app)
                    results["applications_processed"] += 1
                    self.state.daily_application_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing application {app.id}: {e}")
                    results["errors"].append(f"Application processing error: {e}")
        
        except Exception as e:
            logger.error(f"Error processing applications: {e}")
            results["errors"].append(f"Application processing error: {e}")
    
    async def _process_application(self, application: JobApplication) -> None:
        """Process a single application."""
        logger.info(f"Processing application: {application.position} at {application.company}")
        
        try:
            # Parse job description
            job_desc = self.resume_tailor.parse_job_description(application.job_description)
            job_desc.company = application.company
            job_desc.title = application.position
            job_desc.location = application.location
            
            # Generate tailored resume
            tailored_resume = self.resume_tailor.tailor_resume(job_desc)
            
            # Generate cover letter
            cover_letter = self.resume_tailor.generate_cover_letter(job_desc)
            
            # Generate recruiter message
            contact = ContactInfo(
                name=application.recruiter_name or "Hiring Manager",
                company=application.company,
                role="Recruiter",
                location=application.location,
                connection_type="recruiter",
                mutual_connections=0,
                shared_experience="Data Engineering"
            )
            
            recruiter_message = self.messaging.generate_recruiter_email(
                contact, application.position, application.job_description
            )
            
            # Update application with generated content
            self.job_tracker.update_application(application.id, {
                "status": "ready_to_apply",
                "notes": f"Tailored resume and cover letter generated. Recruiter message: {recruiter_message[:200]}..."
            })
            
            logger.info(f"Application processed successfully: {application.company} - {application.position}")
            
        except Exception as e:
            logger.error(f"Error processing application {application.id}: {e}")
            raise
    
    async def _update_application_statuses(self, results: Dict[str, Any]) -> None:
        """Update application statuses based on time and activity."""
        logger.info("Updating application statuses...")
        
        try:
            # Get applications that might need status updates
            applications = self.job_tracker.get_applications(status="applied")
            
            for app in applications:
                try:
                    # Check if application is old enough to follow up
                    app_date = datetime.strptime(app.application_date, "%Y-%m-%d")
                    days_since_applied = (datetime.now() - app_date).days
                    
                    if days_since_applied >= 7 and app.status == "applied":
                        # Update to under review
                        self.job_tracker.update_application(app.id, {
                            "status": "under_review",
                            "follow_up_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                        })
                        logger.info(f"Updated status for {app.company} - {app.position} to under_review")
                    
                except Exception as e:
                    logger.error(f"Error updating status for application {app.id}: {e}")
                    results["errors"].append(f"Status update error: {e}")
        
        except Exception as e:
            logger.error(f"Error updating application statuses: {e}")
            results["errors"].append(f"Status update error: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "status": self.state.status,
            "current_task": self.state.current_task,
            "daily_application_count": self.state.daily_application_count,
            "last_activity": self.state.last_activity,
            "search_criteria": {
                "keywords": self.search_criteria.keywords,
                "companies": self.search_criteria.companies,
                "locations": self.search_criteria.locations
            }
        }
    
    def update_search_criteria(self, new_criteria: Dict[str, Any]) -> None:
        """Update search criteria."""
        if "keywords" in new_criteria:
            self.search_criteria.keywords = new_criteria["keywords"]
        if "companies" in new_criteria:
            self.search_criteria.companies = new_criteria["companies"]
        if "locations" in new_criteria:
            self.search_criteria.locations = new_criteria["locations"]
        if "salary_range" in new_criteria:
            self.search_criteria.salary_range = tuple(new_criteria["salary_range"])
        
        logger.info("Search criteria updated")
    
    def pause_agent(self) -> None:
        """Pause the agent."""
        self.state.status = "paused"
        logger.info("Agent paused")
    
    def resume_agent(self) -> None:
        """Resume the agent."""
        self.state.status = "idle"
        logger.info("Agent resumed")
    
    def stop_agent(self) -> None:
        """Stop the agent."""
        self.state.status = "stopped"
        logger.info("Agent stopped")

def main():
    """Main function for testing the agent."""
    # Initialize agent
    agent = JobSearchAgent()
    
    # Run daily workflow
    print("Running daily workflow...")
    results = asyncio.run(agent.run_daily_workflow())
    print(f"Workflow results: {results}")
    
    # Get agent status
    status = agent.get_agent_status()
    print(f"Agent status: {status}")

if __name__ == "__main__":
    main()
