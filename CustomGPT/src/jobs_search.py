"""
Job Search Service using SerpAPI
Searches for ML Engineer, ML Infrastructure Engineer, and Data Scientist positions
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobSearchService:
    """
    Service for searching job postings using SerpAPI.
    Searches LinkedIn Jobs via Google Jobs API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the job search service.
        
        Args:
            api_key: SerpAPI key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SerpAPI key missing. Set SERPAPI_KEY environment variable.")
        
        if GoogleSearch is None:
            raise ImportError("google-search-results package not installed. Run: pip install google-search-results")
    
    def search_jobs(
        self, 
        query: str = "ML Engineer", 
        location: str = "United States", 
        limit: int = 10,
        experience_level: Optional[str] = None,
        job_type: Optional[str] = None,
        remote: bool = False
    ) -> pd.DataFrame:
        """
        Search for job postings using SerpAPI.
        
        Args:
            query: Job title to search for
            location: Location to search in
            limit: Maximum number of results to return
            experience_level: Experience level filter (entry, mid, senior, executive)
            job_type: Job type filter (full-time, part-time, contract, internship)
            remote: Whether to include remote jobs
            
        Returns:
            DataFrame with job search results
        """
        logger.info(f"Searching for jobs: '{query}' in '{location}'")
        
        # Build search parameters
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": location,
            "hl": "en",
            "api_key": self.api_key,
            "num": min(limit, 100)  # SerpAPI limit
        }
        
        # Add optional filters
        if experience_level:
            params["chips"] = f"date_posted:{experience_level}"
        
        if job_type:
            params["chips"] = f"{params.get('chips', '')},employment_type:{job_type}"
        
        if remote:
            params["chips"] = f"{params.get('chips', '')},remote"
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract job results
            jobs = results.get("jobs_results", [])
            
            if not jobs:
                logger.warning("No job results found")
                return pd.DataFrame()
            
            # Process job data
            jobs_data = []
            for job in jobs[:limit]:
                job_data = {
                    "title": job.get("title", ""),
                    "company": job.get("company_name", ""),
                    "location": job.get("location", ""),
                    "description": job.get("description", ""),
                    "link": job.get("apply_link", ""),
                    "via": job.get("via", ""),
                    "date_posted": job.get("detected_extensions", {}).get("posted_at", ""),
                    "schedule_type": job.get("detected_extensions", {}).get("schedule_type", ""),
                    "salary": job.get("detected_extensions", {}).get("salary", ""),
                    "date_collected": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "search_query": query,
                    "search_location": location
                }
                jobs_data.append(job_data)
            
            df = pd.DataFrame(jobs_data)
            logger.info(f"Found {len(df)} job results")
            return df
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return pd.DataFrame()
    
    def search_multiple_queries(
        self, 
        queries: List[str], 
        location: str = "United States", 
        limit_per_query: int = 5
    ) -> pd.DataFrame:
        """
        Search for multiple job queries and combine results.
        
        Args:
            queries: List of job titles to search for
            location: Location to search in
            limit_per_query: Maximum results per query
            
        Returns:
            Combined DataFrame with all job results
        """
        all_results = []
        
        for query in queries:
            logger.info(f"Searching for: {query}")
            results = self.search_jobs(query, location, limit_per_query)
            if not results.empty:
                all_results.append(results)
        
        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            # Remove duplicates based on title and company
            combined_df = combined_df.drop_duplicates(subset=['title', 'company'], keep='first')
            logger.info(f"Combined search found {len(combined_df)} unique jobs")
            return combined_df
        else:
            return pd.DataFrame()
    
    def search_target_roles(
        self, 
        location: str = "United States", 
        limit_per_role: int = 5
    ) -> pd.DataFrame:
        """
        Search for all target roles from configuration.
        
        Args:
            location: Location to search in
            limit_per_role: Maximum results per role
            
        Returns:
            DataFrame with job results for all target roles
        """
        # Target roles from your configuration
        target_roles = [
            "ML Engineer",
            "Senior ML Engineer", 
            "ML Platform Engineer",
            "ML Infrastructure Engineer",
            "Data Scientist",
            "Senior Data Scientist",
            "Staff ML Engineer",
            "Principal ML Engineer"
        ]
        
        return self.search_multiple_queries(target_roles, location, limit_per_role)
    
    def search_by_company(
        self, 
        company: str, 
        location: str = "United States", 
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Search for jobs at a specific company.
        
        Args:
            company: Company name to search for
            location: Location to search in
            limit: Maximum number of results
            
        Returns:
            DataFrame with job results for the company
        """
        query = f"{company} ML Engineer OR {company} Data Scientist OR {company} ML Infrastructure Engineer"
        return self.search_jobs(query, location, limit)
    
    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific job posting.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary with detailed job information
        """
        # This would require additional implementation
        # For now, return basic info
        return {
            "url": job_url,
            "status": "details_not_implemented",
            "note": "Use the job URL to view full details"
        }

def create_job_application_from_search(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert job search result to job application format.
    
    Args:
        job_data: Job data from search results
        
    Returns:
        Dictionary in job application format
    """
    return {
        "company": job_data.get("company", ""),
        "position": job_data.get("title", ""),
        "location": job_data.get("location", ""),
        "job_description": job_data.get("description", ""),
        "job_url": job_data.get("link", ""),
        "application_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "new",
        "priority": "medium",
        "source": "job_search",
        "notes": f"Found via {job_data.get('via', 'job search')} on {job_data.get('date_collected', '')}"
    }

# Example usage
if __name__ == "__main__":
    # Test the job search service
    try:
        service = JobSearchService()
        
        # Search for ML Engineer jobs
        results = service.search_jobs("ML Engineer", "San Francisco, CA", 5)
        print(f"Found {len(results)} jobs")
        if not results.empty:
            print(results[['title', 'company', 'location']].head())
        
        # Search for multiple roles
        multi_results = service.search_multiple_queries(
            ["ML Engineer", "Data Scientist"], 
            "United States", 
            3
        )
        print(f"Found {len(multi_results)} total jobs across roles")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set SERPAPI_KEY environment variable")
