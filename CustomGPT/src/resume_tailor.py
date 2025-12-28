"""
Resume Tailoring Tool for Srivatsav Job Search GPT
Automatically customizes resume content based on job descriptions and requirements.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import yaml
import os

from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobDescription:
    """Data class for job description information."""
    title: str
    company: str
    location: str
    requirements: List[str]
    responsibilities: List[str]
    skills: List[str]
    experience_level: str
    description_text: str

@dataclass
class ResumeSection:
    """Data class for resume section information."""
    section_name: str
    content: str
    keywords: List[str]
    relevance_score: float

class ResumeTailor:
    """
    Resume tailoring tool that customizes resume content based on job descriptions.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the resume tailor with configuration."""
        self.config = self._load_config(config_path)
        # Initialize LLM based on configuration
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openrouter")
        
        if provider == "openrouter":
            # Use OpenRouter API
            self.llm = ChatOpenAI(
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                model_name=llm_config.get("model", "anthropic/claude-3.5-sonnet"),
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=1500,
                openai_api_base=llm_config.get("base_url", "https://openrouter.ai/api/v1")
            )
        else:
            # Use OpenAI API
            self.llm = OpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model_name=self.config.get("openai", {}).get("model", "gpt-4o"),
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=1500
            )
        
        # Load base resume content
        self.base_resume = self._load_base_resume()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _load_base_resume(self) -> str:
        """Load the base resume content."""
        try:
            with open("data/resume.md", "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error loading base resume: {e}")
            return ""
    
    def parse_job_description(self, job_text: str) -> JobDescription:
        """
        Parse job description text to extract structured information.
        
        Args:
            job_text: Raw job description text
            
        Returns:
            JobDescription object with parsed information
        """
        logger.info("Parsing job description...")
        
        # Create prompt for job description parsing
        parse_prompt = PromptTemplate(
            input_variables=["job_text"],
            template="""
            Parse the following job description and extract structured information. Return the information in the specified format.

            Job Description:
            {job_text}

            Extract and return:
            1. Job Title
            2. Company Name
            3. Location
            4. Required Skills (list)
            5. Key Responsibilities (list)
            6. Technical Skills (list)
            7. Experience Level Required
            8. Any other relevant information

            Format your response as:
            TITLE: [job title]
            COMPANY: [company name]
            LOCATION: [location]
            REQUIREMENTS: [list of requirements, one per line]
            RESPONSIBILITIES: [list of responsibilities, one per line]
            SKILLS: [list of technical skills, one per line]
            EXPERIENCE_LEVEL: [experience level]
            """
        )
        
        try:
            response = self.llm.invoke(parse_prompt.format(job_text=job_text))
            
            # Handle different response types
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Parse the response
            lines = response_text.strip().split('\n')
            job_info = {
                'title': '',
                'company': '',
                'location': '',
                'requirements': [],
                'responsibilities': [],
                'skills': [],
                'experience_level': '',
                'description_text': job_text
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('TITLE:'):
                    job_info['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('COMPANY:'):
                    job_info['company'] = line.replace('COMPANY:', '').strip()
                elif line.startswith('LOCATION:'):
                    job_info['location'] = line.replace('LOCATION:', '').strip()
                elif line.startswith('REQUIREMENTS:'):
                    current_section = 'requirements'
                elif line.startswith('RESPONSIBILITIES:'):
                    current_section = 'responsibilities'
                elif line.startswith('SKILLS:'):
                    current_section = 'skills'
                elif line.startswith('EXPERIENCE_LEVEL:'):
                    job_info['experience_level'] = line.replace('EXPERIENCE_LEVEL:', '').strip()
                elif current_section and line:
                    job_info[current_section].append(line)
            
            return JobDescription(**job_info)
            
        except Exception as e:
            logger.error(f"Error parsing job description: {e}")
            return JobDescription(
                title="Unknown",
                company="Unknown",
                location="Unknown",
                requirements=[],
                responsibilities=[],
                skills=[],
                experience_level="Unknown",
                description_text=job_text
            )
    
    def analyze_resume_sections(self, job_desc: JobDescription) -> List[ResumeSection]:
        """
        Analyze resume sections for relevance to job description.
        
        Args:
            job_desc: Parsed job description
            
        Returns:
            List of ResumeSection objects with relevance scores
        """
        logger.info("Analyzing resume sections...")
        
        # Split resume into sections
        sections = self._split_resume_into_sections()
        
        analyzed_sections = []
        for section_name, content in sections.items():
            if not content.strip():
                continue
                
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(content, job_desc)
            
            # Extract keywords
            keywords = self._extract_keywords(content, job_desc)
            
            analyzed_sections.append(ResumeSection(
                section_name=section_name,
                content=content,
                keywords=keywords,
                relevance_score=relevance_score
            ))
        
        # Sort by relevance score
        analyzed_sections.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return analyzed_sections
    
    def _split_resume_into_sections(self) -> Dict[str, str]:
        """Split resume into sections based on headers."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in self.base_resume.split('\n'):
            if line.startswith('#'):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.strip('# ').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _calculate_relevance_score(self, content: str, job_desc: JobDescription) -> float:
        """Calculate relevance score for resume content against job description."""
        # Combine all job description text
        job_text = ' '.join([
            job_desc.title,
            job_desc.company,
            ' '.join(job_desc.requirements),
            ' '.join(job_desc.responsibilities),
            ' '.join(job_desc.skills)
        ]).lower()
        
        # Count keyword matches
        content_lower = content.lower()
        matches = 0
        total_keywords = 0
        
        # Check for skill matches
        for skill in job_desc.skills:
            total_keywords += 1
            if skill.lower() in content_lower:
                matches += 1
        
        # Check for requirement matches
        for req in job_desc.requirements:
            total_keywords += 1
            if any(word.lower() in content_lower for word in req.split()):
                matches += 1
        
        # Calculate score
        if total_keywords == 0:
            return 0.0
        
        return matches / total_keywords
    
    def _extract_keywords(self, content: str, job_desc: JobDescription) -> List[str]:
        """Extract relevant keywords from content."""
        keywords = []
        content_lower = content.lower()
        
        # Check for skill matches
        for skill in job_desc.skills:
            if skill.lower() in content_lower:
                keywords.append(skill)
        
        # Check for requirement matches
        for req in job_desc.requirements:
            words = req.split()
            for word in words:
                if word.lower() in content_lower and len(word) > 3:
                    keywords.append(word)
        
        return list(set(keywords))
    
    def tailor_resume(self, job_desc: JobDescription) -> str:
        """
        Tailor resume content for a specific job description.
        
        Args:
            job_desc: Parsed job description
            
        Returns:
            Tailored resume content
        """
        logger.info(f"Tailoring resume for {job_desc.title} at {job_desc.company}")
        
        # Analyze resume sections
        sections = self.analyze_resume_sections(job_desc)
        
        # Create tailored resume
        tailored_resume = self._create_tailored_resume(job_desc, sections)
        
        return tailored_resume
    
    def _create_tailored_resume(self, job_desc: JobDescription, sections: List[ResumeSection]) -> str:
        """Create tailored resume content."""
        
        # Create prompt for resume tailoring
        tailor_prompt = PromptTemplate(
            input_variables=["base_resume", "job_desc", "sections"],
            template="""
            You are Srivatsav's AI Job Search Advisor. Tailor the following resume for the specific job description provided.

            Job Description:
            Title: {job_desc.title}
            Company: {job_desc.company}
            Location: {job_desc.location}
            Requirements: {job_desc.requirements}
            Responsibilities: {job_desc.responsibilities}
            Skills: {job_desc.skills}
            Experience Level: {job_desc.experience_level}

            Base Resume:
            {base_resume}

            Resume Section Analysis:
            {sections}

            Instructions:
            1. Keep the same overall structure and format
            2. Emphasize experiences and skills that match the job requirements
            3. Add relevant keywords from the job description
            4. Quantify achievements where possible
            5. Highlight leadership and technical skills that align with the role
            6. Ensure the professional summary reflects the target role
            7. Prioritize experiences that demonstrate the required skills

            Return the tailored resume in the same markdown format.
            """
        )
        
        try:
            # Format sections for prompt
            sections_text = "\n".join([
                f"Section: {s.section_name}\nRelevance: {s.relevance_score:.2f}\nKeywords: {', '.join(s.keywords)}\n"
                for s in sections[:5]  # Top 5 most relevant sections
            ])
            
            response = self.llm.invoke(tailor_prompt.format(
                base_resume=self.base_resume,
                job_desc=job_desc,
                sections=sections_text
            ))
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Error tailoring resume: {e}")
            return self.base_resume  # Return original if error
    
    def generate_cover_letter(self, job_desc: JobDescription) -> str:
        """
        Generate a tailored cover letter for a job description.
        
        Args:
            job_desc: Parsed job description
            
        Returns:
            Generated cover letter
        """
        logger.info(f"Generating cover letter for {job_desc.title} at {job_desc.company}")
        
        # Create prompt for cover letter generation
        cover_letter_prompt = PromptTemplate(
            input_variables=["job_desc", "base_resume"],
            template="""
            You are Srivatsav's AI Job Search Advisor. Generate a professional cover letter for the following job application.

            Job Description:
            Title: {job_desc.title}
            Company: {job_desc.company}
            Location: {job_desc.location}
            Requirements: {job_desc.requirements}
            Responsibilities: {job_desc.responsibilities}
            Skills: {job_desc.skills}

            Srivatsav's Background:
            {base_resume}

            Instructions:
            1. Write a professional, engaging cover letter
            2. Highlight 2-3 most relevant achievements
            3. Show enthusiasm for the company and role
            4. Demonstrate understanding of the company's needs
            5. Include specific examples of relevant experience
            6. Keep it concise (3-4 paragraphs)
            7. Use a professional but personable tone

            Return the cover letter in proper business letter format.
            """
        )
        
        try:
            response = self.llm.invoke(cover_letter_prompt.format(
                job_desc=job_desc,
                base_resume=self.base_resume
            ))
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return "Error generating cover letter"
    
    def get_tailoring_suggestions(self, job_desc: JobDescription) -> List[str]:
        """
        Get suggestions for improving resume tailoring.
        
        Args:
            job_desc: Parsed job description
            
        Returns:
            List of suggestions
        """
        logger.info("Generating tailoring suggestions...")
        
        # Create prompt for suggestions
        suggestions_prompt = PromptTemplate(
            input_variables=["job_desc", "base_resume"],
            template="""
            You are Srivatsav's AI Job Search Advisor. Analyze the job description and current resume to provide specific suggestions for improvement.

            Job Description:
            Title: {job_desc.title}
            Company: {job_desc.company}
            Requirements: {job_desc.requirements}
            Responsibilities: {job_desc.responsibilities}
            Skills: {job_desc.skills}

            Current Resume:
            {base_resume}

            Provide 5-7 specific, actionable suggestions for tailoring the resume to this job. Focus on:
            1. Skills to emphasize or add
            2. Experiences to highlight
            3. Keywords to include
            4. Achievements to quantify
            5. Formatting or structure improvements

            Return each suggestion as a bullet point.
            """
        )
        
        try:
            response = self.llm.invoke(suggestions_prompt.format(
                job_desc=job_desc,
                base_resume=self.base_resume
            ))
            
            # Handle different response types
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Parse suggestions
            suggestions = [line.strip() for line in response_text.split('\n') if line.strip().startswith('•') or line.strip().startswith('-')]
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return ["Error generating suggestions"]

def main():
    """Main function for testing the resume tailor."""
    # Sample job description
    sample_job = """
    Senior Data Engineer - Google
    Mountain View, CA
    
    We are looking for a Senior Data Engineer to join our data platform team. You will be responsible for building and maintaining large-scale data pipelines, optimizing data warehouse performance, and enabling data-driven decision making across the organization.
    
    Requirements:
    - 5+ years of experience in data engineering
    - Strong experience with Google Cloud Platform (GCP)
    - Proficiency in Python, SQL, and Apache Airflow
    - Experience with BigQuery and data warehousing
    - Knowledge of machine learning pipelines and MLOps
    - Experience with real-time data processing
    - Strong problem-solving and communication skills
    
    Responsibilities:
    - Design and implement scalable data pipelines
    - Optimize BigQuery performance and reduce costs
    - Build ML model deployment pipelines
    - Mentor junior engineers
    - Collaborate with data scientists and product teams
    """
    
    # Initialize resume tailor
    tailor = ResumeTailor()
    
    # Parse job description
    job_desc = tailor.parse_job_description(sample_job)
    print(f"Parsed Job: {job_desc.title} at {job_desc.company}")
    print(f"Skills: {job_desc.skills}")
    print(f"Requirements: {job_desc.requirements}")
    
    # Generate tailored resume
    tailored_resume = tailor.tailor_resume(job_desc)
    print("\n" + "="*80)
    print("TAILORED RESUME")
    print("="*80)
    print(tailored_resume)
    
    # Generate cover letter
    cover_letter = tailor.generate_cover_letter(job_desc)
    print("\n" + "="*80)
    print("COVER LETTER")
    print("="*80)
    print(cover_letter)
    
    # Get suggestions
    suggestions = tailor.get_tailoring_suggestions(job_desc)
    print("\n" + "="*80)
    print("TAILORING SUGGESTIONS")
    print("="*80)
    for suggestion in suggestions:
        print(f"• {suggestion}")

if __name__ == "__main__":
    main()
