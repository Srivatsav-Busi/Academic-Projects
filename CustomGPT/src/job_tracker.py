"""
Job Tracking System for Srivatsav Job Search GPT
Manages job applications, responses, and interview tracking.
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobApplication:
    """Data class for job application information."""
    id: Optional[int] = None
    company: str = ""
    position: str = ""
    location: str = ""
    job_url: str = ""
    job_description: str = ""
    application_date: str = ""
    status: str = "applied"  # applied, under_review, interview_scheduled, rejected, offer_received
    priority: str = "medium"  # high, medium, low
    salary_range: str = ""
    notes: str = ""
    recruiter_name: str = ""
    recruiter_email: str = ""
    follow_up_date: str = ""
    interview_date: str = ""
    interview_type: str = ""  # phone, video, onsite
    interview_notes: str = ""
    rejection_reason: str = ""
    offer_amount: str = ""
    created_at: str = ""
    updated_at: str = ""

@dataclass
class Interview:
    """Data class for interview information."""
    id: Optional[int] = None
    application_id: int = 0
    interview_date: str = ""
    interview_type: str = ""
    interviewer_name: str = ""
    interviewer_title: str = ""
    questions_asked: str = ""
    my_answers: str = ""
    feedback_received: str = ""
    next_steps: str = ""
    preparation_notes: str = ""
    created_at: str = ""
    updated_at: str = ""

class JobTracker:
    """
    Job tracking system for managing applications and interviews.
    """
    
    def __init__(self, db_path: str = "data/job_tracker.db"):
        """Initialize the job tracker with database path."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create job_applications table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company TEXT NOT NULL,
                        position TEXT NOT NULL,
                        location TEXT,
                        job_url TEXT,
                        job_description TEXT,
                        application_date TEXT,
                        status TEXT DEFAULT 'applied',
                        priority TEXT DEFAULT 'medium',
                        salary_range TEXT,
                        notes TEXT,
                        recruiter_name TEXT,
                        recruiter_email TEXT,
                        follow_up_date TEXT,
                        interview_date TEXT,
                        interview_type TEXT,
                        interview_notes TEXT,
                        rejection_reason TEXT,
                        offer_amount TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create interviews table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS interviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        application_id INTEGER,
                        interview_date TEXT,
                        interview_type TEXT,
                        interviewer_name TEXT,
                        interviewer_title TEXT,
                        questions_asked TEXT,
                        my_answers TEXT,
                        feedback_received TEXT,
                        next_steps TEXT,
                        preparation_notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (application_id) REFERENCES job_applications (id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_company ON job_applications(company)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON job_applications(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_application_date ON job_applications(application_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_application_id ON interviews(application_id)")
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_application(self, application: JobApplication) -> int:
        """
        Add a new job application to the tracker.
        
        Args:
            application: JobApplication object
            
        Returns:
            ID of the created application
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Set timestamps
                now = datetime.now().isoformat()
                application.created_at = now
                application.updated_at = now
                
                # Insert application
                cursor.execute("""
                    INSERT INTO job_applications (
                        company, position, location, job_url, job_description,
                        application_date, status, priority, salary_range, notes,
                        recruiter_name, recruiter_email, follow_up_date,
                        interview_date, interview_type, interview_notes,
                        rejection_reason, offer_amount, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    application.company, application.position, application.location,
                    application.job_url, application.job_description, application.application_date,
                    application.status, application.priority, application.salary_range,
                    application.notes, application.recruiter_name, application.recruiter_email,
                    application.follow_up_date, application.interview_date, application.interview_type,
                    application.interview_notes, application.rejection_reason, application.offer_amount,
                    application.created_at, application.updated_at
                ))
                
                application_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Added application for {application.position} at {application.company}")
                return application_id
                
        except Exception as e:
            logger.error(f"Error adding application: {e}")
            raise
    
    def get_application(self, application_id: int) -> Optional[JobApplication]:
        """
        Get a job application by ID.
        
        Args:
            application_id: ID of the application
            
        Returns:
            JobApplication object or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM job_applications WHERE id = ?", (application_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_application(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting application: {e}")
            return None
    
    def get_applications(self, status: str = None, company: str = None, limit: int = 50) -> List[JobApplication]:
        """
        Get job applications with optional filters.
        
        Args:
            status: Filter by status
            company: Filter by company
            limit: Maximum number of applications to return
            
        Returns:
            List of JobApplication objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM job_applications WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if company:
                    query += " AND company LIKE ?"
                    params.append(f"%{company}%")
                
                query += " ORDER BY application_date DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                applications = [self._row_to_application(row) for row in rows]
                return applications
                
        except Exception as e:
            logger.error(f"Error getting applications: {e}")
            return []
    
    def update_application(self, application_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a job application.
        
        Args:
            application_id: ID of the application to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add updated_at timestamp
                updates['updated_at'] = datetime.now().isoformat()
                
                # Build update query
                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                query = f"UPDATE job_applications SET {set_clause} WHERE id = ?"
                
                params = list(updates.values()) + [application_id]
                cursor.execute(query, params)
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Updated application {application_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error updating application: {e}")
            return False
    
    def delete_application(self, application_id: int) -> bool:
        """
        Delete a job application.
        
        Args:
            application_id: ID of the application to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete associated interviews first
                cursor.execute("DELETE FROM interviews WHERE application_id = ?", (application_id,))
                
                # Delete application
                cursor.execute("DELETE FROM job_applications WHERE id = ?", (application_id,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Deleted application {application_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting application: {e}")
            return False
    
    def add_interview(self, interview: Interview) -> int:
        """
        Add a new interview to the tracker.
        
        Args:
            interview: Interview object
            
        Returns:
            ID of the created interview
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Set timestamps
                now = datetime.now().isoformat()
                interview.created_at = now
                interview.updated_at = now
                
                # Insert interview
                cursor.execute("""
                    INSERT INTO interviews (
                        application_id, interview_date, interview_type,
                        interviewer_name, interviewer_title, questions_asked,
                        my_answers, feedback_received, next_steps,
                        preparation_notes, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interview.application_id, interview.interview_date, interview.interview_type,
                    interview.interviewer_name, interview.interviewer_title, interview.questions_asked,
                    interview.my_answers, interview.feedback_received, interview.next_steps,
                    interview.preparation_notes, interview.created_at, interview.updated_at
                ))
                
                interview_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Added interview for application {interview.application_id}")
                return interview_id
                
        except Exception as e:
            logger.error(f"Error adding interview: {e}")
            raise
    
    def get_interviews(self, application_id: int = None) -> List[Interview]:
        """
        Get interviews, optionally filtered by application ID.
        
        Args:
            application_id: Filter by application ID
            
        Returns:
            List of Interview objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if application_id:
                    cursor.execute("SELECT * FROM interviews WHERE application_id = ? ORDER BY interview_date DESC", (application_id,))
                else:
                    cursor.execute("SELECT * FROM interviews ORDER BY interview_date DESC")
                
                rows = cursor.fetchall()
                interviews = [self._row_to_interview(row) for row in rows]
                return interviews
                
        except Exception as e:
            logger.error(f"Error getting interviews: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get job search statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total applications
                cursor.execute("SELECT COUNT(*) FROM job_applications")
                total_applications = cursor.fetchone()[0]
                
                # Applications by status
                cursor.execute("SELECT status, COUNT(*) FROM job_applications GROUP BY status")
                status_counts = dict(cursor.fetchall())
                
                # Applications by company
                cursor.execute("SELECT company, COUNT(*) FROM job_applications GROUP BY company ORDER BY COUNT(*) DESC LIMIT 10")
                company_counts = dict(cursor.fetchall())
                
                # Applications by month
                cursor.execute("""
                    SELECT strftime('%Y-%m', application_date) as month, COUNT(*) 
                    FROM job_applications 
                    GROUP BY month 
                    ORDER BY month DESC 
                    LIMIT 12
                """)
                monthly_counts = dict(cursor.fetchall())
                
                # Total interviews
                cursor.execute("SELECT COUNT(*) FROM interviews")
                total_interviews = cursor.fetchone()[0]
                
                # Response rate
                responded = status_counts.get('interview_scheduled', 0) + status_counts.get('rejected', 0) + status_counts.get('offer_received', 0)
                response_rate = (responded / total_applications * 100) if total_applications > 0 else 0
                
                return {
                    'total_applications': total_applications,
                    'status_counts': status_counts,
                    'company_counts': company_counts,
                    'monthly_counts': monthly_counts,
                    'total_interviews': total_interviews,
                    'response_rate': round(response_rate, 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_follow_up_reminders(self, days_ahead: int = 7) -> List[JobApplication]:
        """
        Get applications that need follow-up.
        
        Args:
            days_ahead: Number of days ahead to check for follow-ups
            
        Returns:
            List of applications needing follow-up
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get applications that need follow-up
                cursor.execute("""
                    SELECT * FROM job_applications 
                    WHERE follow_up_date IS NOT NULL 
                    AND follow_up_date <= date('now', '+{} days')
                    AND status IN ('applied', 'under_review')
                    ORDER BY follow_up_date ASC
                """.format(days_ahead))
                
                rows = cursor.fetchall()
                applications = [self._row_to_application(row) for row in rows]
                return applications
                
        except Exception as e:
            logger.error(f"Error getting follow-up reminders: {e}")
            return []
    
    def _row_to_application(self, row: Tuple) -> JobApplication:
        """Convert database row to JobApplication object."""
        return JobApplication(
            id=row[0],
            company=row[1],
            position=row[2],
            location=row[3],
            job_url=row[4],
            job_description=row[5],
            application_date=row[6],
            status=row[7],
            priority=row[8],
            salary_range=row[9],
            notes=row[10],
            recruiter_name=row[11],
            recruiter_email=row[12],
            follow_up_date=row[13],
            interview_date=row[14],
            interview_type=row[15],
            interview_notes=row[16],
            rejection_reason=row[17],
            offer_amount=row[18],
            created_at=row[19],
            updated_at=row[20]
        )
    
    def _row_to_interview(self, row: Tuple) -> Interview:
        """Convert database row to Interview object."""
        return Interview(
            id=row[0],
            application_id=row[1],
            interview_date=row[2],
            interview_type=row[3],
            interviewer_name=row[4],
            interviewer_title=row[5],
            questions_asked=row[6],
            my_answers=row[7],
            feedback_received=row[8],
            next_steps=row[9],
            preparation_notes=row[10],
            created_at=row[11],
            updated_at=row[12]
        )

def main():
    """Main function for testing the job tracker."""
    # Initialize job tracker
    tracker = JobTracker()
    
    # Create sample application
    application = JobApplication(
        company="Google",
        position="Senior Data Engineer",
        location="Mountain View, CA",
        job_url="https://careers.google.com/jobs/results/123456",
        job_description="Looking for a Senior Data Engineer with GCP experience...",
        application_date="2024-01-15",
        status="applied",
        priority="high",
        salary_range="$180K-$220K",
        notes="Applied through LinkedIn",
        recruiter_name="Sarah Johnson",
        recruiter_email="sarah.johnson@google.com",
        follow_up_date="2024-01-22"
    )
    
    # Add application
    app_id = tracker.add_application(application)
    print(f"Added application with ID: {app_id}")
    
    # Get applications
    applications = tracker.get_applications()
    print(f"Total applications: {len(applications)}")
    
    # Get statistics
    stats = tracker.get_statistics()
    print(f"Statistics: {stats}")
    
    # Create sample interview
    interview = Interview(
        application_id=app_id,
        interview_date="2024-01-25",
        interview_type="phone",
        interviewer_name="John Smith",
        interviewer_title="Hiring Manager",
        questions_asked="Tell me about your experience with BigQuery",
        my_answers="I have 3+ years of experience with BigQuery...",
        next_steps="Technical interview next week"
    )
    
    # Add interview
    interview_id = tracker.add_interview(interview)
    print(f"Added interview with ID: {interview_id}")
    
    # Get interviews
    interviews = tracker.get_interviews(app_id)
    print(f"Interviews for application {app_id}: {len(interviews)}")

if __name__ == "__main__":
    main()
