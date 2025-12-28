#!/usr/bin/env python3
"""
Test script for automated resume generation functionality.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from resume_tailor import ResumeTailor, JobDescription

def test_resume_generation():
    """Test the resume generation functionality."""
    print("🧪 Testing Resume Generation...")
    
    # Initialize resume tailor
    try:
        tailor = ResumeTailor()
        print("✅ Resume tailor initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing resume tailor: {e}")
        return False
    
    # Sample job description
    sample_job_desc = """
    Senior Machine Learning Engineer
    
    We are looking for a Senior ML Engineer with experience in:
    - Python, TensorFlow, PyTorch
    - MLOps and model deployment
    - Cloud platforms (AWS, GCP)
    - Distributed computing
    - Data pipelines and ETL
    
    Requirements:
    - 5+ years ML experience
    - Experience with production ML systems
    - Strong software engineering skills
    - Experience with Kubernetes and Docker
    """
    
    try:
        # Parse job description
        job_desc = tailor.parse_job_description(sample_job_desc)
        print("✅ Job description parsed successfully")
        print(f"   - Title: {job_desc.title}")
        print(f"   - Skills: {len(job_desc.skills)} skills found")
        print(f"   - Requirements: {len(job_desc.requirements)} requirements found")
        
        # Generate tailored resume
        tailored_resume = tailor.tailor_resume(job_desc)
        print("✅ Tailored resume generated successfully")
        print(f"   - Resume length: {len(tailored_resume)} characters")
        
        # Save sample resume
        with open("sample_generated_resume.md", "w") as f:
            f.write(tailored_resume)
        print("✅ Sample resume saved to 'sample_generated_resume.md'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating resume: {e}")
        return False

def test_batch_generation():
    """Test batch resume generation with multiple job descriptions."""
    print("\n🧪 Testing Batch Resume Generation...")
    
    # Sample job descriptions
    job_descriptions = [
        {
            "title": "ML Engineer",
            "company": "TechCorp",
            "description": "Looking for ML Engineer with Python, scikit-learn, and cloud experience."
        },
        {
            "title": "Data Scientist",
            "company": "DataCorp", 
            "description": "Seeking Data Scientist with R, Python, and statistical modeling experience."
        },
        {
            "title": "ML Infrastructure Engineer",
            "company": "InfraCorp",
            "description": "Need ML Infrastructure Engineer with Kubernetes, Docker, and MLOps experience."
        }
    ]
    
    try:
        tailor = ResumeTailor()
        generated_resumes = []
        
        for i, job in enumerate(job_descriptions):
            print(f"   Processing job {i+1}/{len(job_descriptions)}: {job['title']} at {job['company']}")
            
            # Parse and generate resume
            job_desc = tailor.parse_job_description(job['description'])
            tailored_resume = tailor.tailor_resume(job_desc)
            
            # Store resume data
            resume_data = {
                'job_title': job['title'],
                'company': job['company'],
                'resume_content': tailored_resume,
                'job_description': job['description'],
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            generated_resumes.append(resume_data)
        
        print(f"✅ Successfully generated {len(generated_resumes)} resumes in batch")
        
        # Save all resumes
        for i, resume in enumerate(generated_resumes):
            filename = f"batch_resume_{i+1}_{resume['company']}_{resume['job_title']}.md"
            with open(filename, "w") as f:
                f.write(resume['resume_content'])
            print(f"   - Saved: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in batch generation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Resume Generation Tests")
    print("=" * 50)
    
    # Test single resume generation
    success1 = test_resume_generation()
    
    # Test batch generation
    success2 = test_batch_generation()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Resume generation is working correctly.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
