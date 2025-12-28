"""
Recruiter Messaging Tool for Srivatsav Job Search GPT
Generates personalized LinkedIn messages and recruiter emails.
"""

import logging
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml
import os

from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContactInfo:
    """Data class for contact information."""
    name: str
    company: str
    role: str
    location: str
    connection_type: str  # 'recruiter', 'hiring_manager', 'employee', 'alumni'
    mutual_connections: int
    shared_experience: str

@dataclass
class MessageContext:
    """Data class for message context."""
    contact: ContactInfo
    target_job: str
    company_research: Dict[str, Any]
    personal_connection: str
    message_type: str  # 'connection_request', 'follow_up', 'thank_you', 'networking'

class RecruiterMessaging:
    """
    Tool for generating personalized recruiter messages and LinkedIn outreach.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the messaging tool with configuration."""
        self.config = self._load_config(config_path)
        # Initialize LLM based on configuration
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openrouter")
        
        if provider == "openrouter":
            # Use OpenRouter API
            self.llm = ChatOpenAI(
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                model_name=llm_config.get("model", "anthropic/claude-3.5-sonnet"),
                temperature=0.7,
                max_tokens=1000,
                openai_api_base=llm_config.get("base_url", "https://openrouter.ai/api/v1")
            )
        else:
            # Use OpenAI API
            self.llm = OpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model_name=self.config.get("openai", {}).get("model", "gpt-4o"),
                temperature=0.7,
                max_tokens=1000
            )
        
        # Load message templates
        self.templates = self._load_templates()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load message templates from files."""
        templates = {}
        
        try:
            # Load LinkedIn templates
            with open("data/recruiter_templates/linkedin_connection_request.md", "r", encoding="utf-8") as file:
                content = file.read()
                templates['linkedin_connection'] = self._parse_templates(content)
            
            # Load email templates
            with open("data/recruiter_templates/recruiter_email_templates.md", "r", encoding="utf-8") as file:
                content = file.read()
                templates['email'] = self._parse_templates(content)
                
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            templates = {'linkedin_connection': [], 'email': []}
        
        return templates
    
    def _parse_templates(self, content: str) -> List[str]:
        """Parse template content into individual templates."""
        templates = []
        current_template = []
        
        for line in content.split('\n'):
            if line.startswith('## Template') or line.startswith('### Template'):
                if current_template:
                    templates.append('\n'.join(current_template))
                    current_template = []
            elif line.strip():
                current_template.append(line)
        
        if current_template:
            templates.append('\n'.join(current_template))
        
        return templates
    
    def generate_linkedin_connection_request(self, contact: ContactInfo, target_job: str = None) -> str:
        """
        Generate a personalized LinkedIn connection request.
        
        Args:
            contact: Contact information
            target_job: Target job title (optional)
            
        Returns:
            Personalized connection request message
        """
        logger.info(f"Generating LinkedIn connection request for {contact.name} at {contact.company}")
        
        # Create prompt for LinkedIn message generation
        prompt = PromptTemplate(
            input_variables=["contact", "target_job", "templates"],
            template="""
            You are Srivatsav's AI Job Search Advisor. Generate a personalized LinkedIn connection request for the following contact.

            Contact Information:
            Name: {contact.name}
            Company: {contact.company}
            Role: {contact.role}
            Location: {contact.location}
            Connection Type: {contact.connection_type}
            Mutual Connections: {contact.mutual_connections}
            Shared Experience: {contact.shared_experience}

            Target Job: {target_job}

            Available Templates:
            {templates}

            Instructions:
            1. Choose the most appropriate template as a starting point
            2. Personalize the message with specific details about the contact and company
            3. Keep it concise (under 200 characters for LinkedIn)
            4. Make it professional but personable
            5. Include a clear reason for connecting
            6. Avoid being too salesy or pushy
            7. Use the contact's name and company appropriately

            Return only the personalized message, no additional text.
            """
        )
        
        try:
            # Select appropriate template
            template = self._select_template('linkedin_connection', contact)
            
            response = self.llm.invoke(prompt.format(
                contact=contact,
                target_job=target_job,
                templates=template
            ))
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                return str(response).strip()
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn message: {e}")
            return self._get_fallback_linkedin_message(contact, target_job)
    
    def generate_recruiter_email(self, contact: ContactInfo, target_job: str, job_description: str = None) -> str:
        """
        Generate a personalized recruiter email.
        
        Args:
            contact: Contact information
            target_job: Target job title
            job_description: Job description text (optional)
            
        Returns:
            Personalized recruiter email
        """
        logger.info(f"Generating recruiter email for {contact.name} at {contact.company}")
        
        # Create prompt for email generation
        prompt = PromptTemplate(
            input_variables=["contact", "target_job", "job_description", "templates"],
            template="""
            You are Srivatsav's AI Job Search Advisor. Generate a personalized recruiter email for the following contact.

            Contact Information:
            Name: {contact.name}
            Company: {contact.company}
            Role: {contact.role}
            Location: {contact.location}
            Connection Type: {contact.connection_type}

            Target Job: {target_job}
            Job Description: {job_description}

            Available Templates:
            {templates}

            Instructions:
            1. Choose the most appropriate template as a starting point
            2. Personalize the email with specific details about the contact and company
            3. Include Srivatsav's relevant experience and achievements
            4. Make it professional and engaging
            5. Include a clear call-to-action
            6. Keep it concise but comprehensive
            7. Use proper business email format

            Return the complete email including subject line.
            """
        )
        
        try:
            # Select appropriate template
            template = self._select_template('email', contact)
            
            response = self.llm.invoke(prompt.format(
                contact=contact,
                target_job=target_job,
                job_description=job_description,
                templates=template
            ))
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                return str(response).strip()
            
        except Exception as e:
            logger.error(f"Error generating recruiter email: {e}")
            return self._get_fallback_email(contact, target_job)
    
    def generate_follow_up_message(self, contact: ContactInfo, target_job: str, days_since_contact: int) -> str:
        """
        Generate a follow-up message for previous contact.
        
        Args:
            contact: Contact information
            target_job: Target job title
            days_since_contact: Days since last contact
            
        Returns:
            Follow-up message
        """
        logger.info(f"Generating follow-up message for {contact.name}")
        
        # Create prompt for follow-up message
        prompt = PromptTemplate(
            input_variables=["contact", "target_job", "days_since_contact"],
            template="""
            You are Srivatsav's AI Job Search Advisor. Generate a follow-up message for a previous contact.

            Contact Information:
            Name: {contact.name}
            Company: {contact.company}
            Role: {contact.role}

            Target Job: {target_job}
            Days Since Last Contact: {days_since_contact}

            Instructions:
            1. Be polite and professional
            2. Reference the previous conversation
            3. Provide additional value or information
            4. Keep it brief and to the point
            5. Include a clear next step
            6. Avoid being pushy or repetitive

            Return the follow-up message.
            """
        )
        
        try:
            response = self.llm.invoke(prompt.format(
                contact=contact,
                target_job=target_job,
                days_since_contact=days_since_contact
            ))
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                return str(response).strip()
            
        except Exception as e:
            logger.error(f"Error generating follow-up message: {e}")
            return self._get_fallback_follow_up(contact, target_job)
    
    def generate_networking_message(self, contact: ContactInfo, event: str = None) -> str:
        """
        Generate a networking message for industry events or connections.
        
        Args:
            contact: Contact information
            event: Event or context for networking
            
        Returns:
            Networking message
        """
        logger.info(f"Generating networking message for {contact.name}")
        
        # Create prompt for networking message
        prompt = PromptTemplate(
            input_variables=["contact", "event"],
            template="""
            You are Srivatsav's AI Job Search Advisor. Generate a networking message for industry connection.

            Contact Information:
            Name: {contact.name}
            Company: {contact.company}
            Role: {contact.role}
            Location: {contact.location}

            Event/Context: {event}

            Instructions:
            1. Be friendly and professional
            2. Show genuine interest in their work
            3. Offer to share insights or help
            4. Keep it conversational
            5. Include a specific reason for reaching out
            6. Avoid immediately asking for job opportunities

            Return the networking message.
            """
        )
        
        try:
            response = self.llm.invoke(prompt.format(
                contact=contact,
                event=event
            ))
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                return str(response).strip()
            
        except Exception as e:
            logger.error(f"Error generating networking message: {e}")
            return self._get_fallback_networking_message(contact, event)
    
    def _select_template(self, template_type: str, contact: ContactInfo) -> str:
        """Select the most appropriate template for the contact."""
        templates = self.templates.get(template_type, [])
        
        if not templates:
            return "No templates available"
        
        # Simple selection logic based on contact type
        if contact.connection_type == 'recruiter':
            # Look for recruiter-specific templates
            for template in templates:
                if 'recruiter' in template.lower():
                    return template
        elif contact.connection_type == 'hiring_manager':
            # Look for hiring manager templates
            for template in templates:
                if 'hiring' in template.lower() or 'manager' in template.lower():
                    return template
        
        # Return random template if no specific match
        return random.choice(templates)
    
    def _get_fallback_linkedin_message(self, contact: ContactInfo, target_job: str) -> str:
        """Get fallback LinkedIn message if generation fails."""
        return f"Hi {contact.name}, I noticed your work at {contact.company} and would love to connect. I'm a Senior Data Engineer with experience in {target_job or 'data engineering'} and would appreciate the opportunity to learn more about your team's work. Best regards, Srivatsav"
    
    def _get_fallback_email(self, contact: ContactInfo, target_job: str) -> str:
        """Get fallback email if generation fails."""
        return f"""Subject: Interest in {target_job} Opportunities at {contact.company}

Hi {contact.name},

I hope this email finds you well. I'm reaching out because I'm very interested in data engineering opportunities at {contact.company}, particularly the {target_job} role.

I'm a Senior Data Engineer with 5+ years of experience building scalable data infrastructure and ML platforms. Currently, I lead the development of real-time data pipelines processing 50M+ events daily at TechCorp Inc.

I would love the opportunity to discuss how my experience could contribute to your team's success. Would you be available for a brief call this week?

Thank you for your time and consideration.

Best regards,
Srivatsav Busi
Senior Data Engineer
Email: srivatsav.busi@email.com
LinkedIn: linkedin.com/in/srivatsavbusi"""
    
    def _get_fallback_follow_up(self, contact: ContactInfo, target_job: str) -> str:
        """Get fallback follow-up message if generation fails."""
        return f"Hi {contact.name}, I wanted to follow up on my previous message about the {target_job} role at {contact.company}. I'm still very interested in the opportunity and would love to discuss how my experience in data engineering could contribute to your team. Best regards, Srivatsav"
    
    def _get_fallback_networking_message(self, contact: ContactInfo, event: str) -> str:
        """Get fallback networking message if generation fails."""
        return f"Hi {contact.name}, I hope you're doing well. I'm reaching out because I'm interested in learning more about your work at {contact.company}. I'm a Senior Data Engineer with experience in building scalable data platforms and would love to connect and share insights. Best regards, Srivatsav"

def main():
    """Main function for testing the messaging tool."""
    # Sample contact information
    contact = ContactInfo(
        name="Sarah Johnson",
        company="Google",
        role="Senior Recruiter",
        location="Mountain View, CA",
        connection_type="recruiter",
        mutual_connections=5,
        shared_experience="Data Engineering"
    )
    
    # Initialize messaging tool
    messaging = RecruiterMessaging()
    
    # Generate LinkedIn connection request
    linkedin_msg = messaging.generate_linkedin_connection_request(contact, "Senior Data Engineer")
    print("LinkedIn Connection Request:")
    print(linkedin_msg)
    print("\n" + "="*80)
    
    # Generate recruiter email
    email = messaging.generate_recruiter_email(contact, "Senior Data Engineer", "Looking for a Senior Data Engineer with GCP experience...")
    print("Recruiter Email:")
    print(email)
    print("\n" + "="*80)
    
    # Generate follow-up message
    follow_up = messaging.generate_follow_up_message(contact, "Senior Data Engineer", 7)
    print("Follow-up Message:")
    print(follow_up)
    print("\n" + "="*80)
    
    # Generate networking message
    networking = messaging.generate_networking_message(contact, "Data Engineering Summit 2023")
    print("Networking Message:")
    print(networking)

if __name__ == "__main__":
    main()
