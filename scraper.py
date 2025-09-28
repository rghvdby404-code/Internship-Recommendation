import pandas as pd
from jobspy import scrape_jobs
import time
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional
import logging

# Set up logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InternshipScraper:
    """
    A class to scrape internship data from various job boards using the jobspy library.
    """
    
    def __init__(self):
        self.sites = ['linkedin', 'indeed']  # Only use most reliable sites
        self.internship_keywords = [
            'intern', 'internship', 'co-op', 'coop', 'trainee', 'apprentice',
            'entry level', 'junior', 'graduate', 'student', 'summer intern'
        ]
    
    def scrape_internships(self, 
                          skills: List[str], 
                          location: str = "Remote", 
                          max_results: int = 100) -> pd.DataFrame:
        """
        Scrape internship data based on user skills and location preference.
        
        Args:
            skills (List[str]): List of user skills
            location (str): Preferred location
            max_results (int): Maximum number of results to fetch
            
        Returns:
            pd.DataFrame: DataFrame containing internship data
        """
        logger.info(f"Starting to scrape internships for skills: {skills}")
        
        all_internships = []
        
        # Create search terms combining skills with internship keywords
        search_terms = self._create_search_terms(skills)
        
        for search_term in search_terms:
            logger.info(f"Searching for: {search_term}")
            
            try:
                # Scrape jobs using jobspy
                jobs = scrape_jobs(
                    site_name=self.sites,
                    search_term=search_term,
                    location=location,
                    results_wanted=min(max_results // len(search_terms), 50),
                    hours_old=168,  # Last 7 days
                    country_indeed='usa'  # Focus on US market
                )
                
                if jobs is not None and not jobs.empty:
                    # Convert DataFrame to list of dictionaries
                    jobs_list = jobs.to_dict('records')
                    # Filter for internships
                    internship_jobs = self._filter_internships(jobs_list)
                    all_internships.extend(internship_jobs)
                    logger.info(f"Found {len(internship_jobs)} internships for '{search_term}'")
                
                # Add delay to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping for '{search_term}': {str(e)}")
                continue
        
        if not all_internships:
            logger.warning("No internships found")
            return pd.DataFrame()
        
        # Convert to DataFrame and clean data
        df = pd.DataFrame(all_internships)
        df = self._clean_and_enhance_data(df, skills)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['title', 'company', 'location'], keep='first')
        
        logger.info(f"Total unique internships found: {len(df)}")
        return df
    
    def _create_search_terms(self, skills: List[str]) -> List[str]:
        """
        Create search terms by combining skills with internship keywords.
        
        Args:
            skills (List[str]): List of user skills
            
        Returns:
            List[str]: List of search terms
        """
        search_terms = []
        
        # Add individual skills with internship keywords
        for skill in skills[:5]:  # Limit to top 5 skills to avoid too many requests
            for keyword in self.internship_keywords[:3]:  # Use top 3 internship keywords
                search_terms.append(f"{skill} {keyword}")
        
        # Add combined skills search
        if len(skills) >= 2:
            combined_skills = " ".join(skills[:3])
            search_terms.append(f"{combined_skills} internship")
        
        return search_terms[:8]  # Limit total search terms
    
    def _filter_internships(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter jobs to keep only internships.
        
        Args:
            jobs (List[Dict]): List of job dictionaries
            
        Returns:
            List[Dict]: Filtered list of internship jobs
        """
        internships = []
        
        for job in jobs:
            # Handle None and NaN values properly
            title = str(job.get('title', '') or '').lower()
            description = str(job.get('description', '') or '').lower()
            
            # Check if it's an internship
            is_internship = any(keyword in title or keyword in description 
                              for keyword in self.internship_keywords)
            
            # Exclude senior/lead positions
            is_not_senior = not any(senior_word in title 
                                  for senior_word in ['senior', 'lead', 'principal', 'manager', 'director'])
            
            if is_internship and is_not_senior:
                internships.append(job)
        
        return internships
    
    def _clean_and_enhance_data(self, df: pd.DataFrame, user_skills: List[str]) -> pd.DataFrame:
        """
        Clean and enhance the scraped data.
        
        Args:
            df (pd.DataFrame): Raw scraped data
            user_skills (List[str]): User's skills for relevance scoring
            
        Returns:
            pd.DataFrame: Cleaned and enhanced data
        """
        if df.empty:
            return df
        
        # Clean company names
        df['company'] = df['company'].fillna('Unknown Company')
        df['company'] = df['company'].str.strip()
        
        # Clean job titles
        df['title'] = df['title'].fillna('Unknown Title')
        df['title'] = df['title'].str.strip()
        
        # Clean locations
        df['location'] = df['location'].fillna('Not specified')
        df['location'] = df['location'].str.strip()
        
        # Extract and clean stipend/salary information
        df['stipend'] = df.apply(self._extract_stipend, axis=1)
        
        # Calculate days old
        df['days_old'] = df.apply(self._calculate_days_old, axis=1)
        
        # Calculate relevance score based on user skills
        df['relevance_score'] = df.apply(
            lambda row: self._calculate_relevance_score(row, user_skills), axis=1
        )
        
        # Clean apply URLs
        df['apply_url'] = df['job_url'].fillna('')
        
        # Select and rename columns
        columns_mapping = {
            'title': 'title',
            'company': 'company',
            'location': 'location',
            'description': 'description',
            'job_url': 'apply_url',
            'stipend': 'stipend',
            'days_old': 'days_old',
            'relevance_score': 'relevance_score'
        }
        
        df = df[list(columns_mapping.keys())].rename(columns=columns_mapping)
        
        return df
    
    def _extract_stipend(self, row) -> float:
        """
        Extract stipend/salary information from job description.
        
        Args:
            row: DataFrame row containing job information
            
        Returns:
            float: Extracted stipend amount
        """
        description = str(row.get('description', '')).lower()
        title = str(row.get('title', '')).lower()
        
        # Look for salary patterns
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,000.00 or $1000
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s+)?(?:hour|hr|/h)',  # hourly rates
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s+)?(?:month|mo)',  # monthly rates
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, description + ' ' + title)
            if matches:
                try:
                    # Take the first match and convert to float
                    amount_str = matches[0].replace(',', '')
                    amount = float(amount_str)
                    
                    # Convert hourly to monthly (assuming 160 hours/month)
                    if 'hour' in description or 'hr' in description or '/h' in description:
                        amount = amount * 160
                    
                    # Convert monthly to yearly (assuming 12 months)
                    if 'month' in description or 'mo' in description:
                        amount = amount * 12
                    
                    # Return monthly equivalent
                    return amount / 12
                    
                except ValueError:
                    continue
        
        return 0.0  # No stipend found
    
    def _calculate_days_old(self, row) -> int:
        """
        Calculate how many days old the job posting is.
        
        Args:
            row: DataFrame row containing job information
            
        Returns:
            int: Number of days old
        """
        date_posted = row.get('date_posted')
        
        if pd.isna(date_posted) or date_posted is None:
            return 999  # Unknown age
        
        try:
            if isinstance(date_posted, str):
                # Try to parse the date string
                date_posted = pd.to_datetime(date_posted)
            
            days_old = (datetime.now() - date_posted).days
            return max(0, days_old)
            
        except Exception:
            return 999  # Unknown age
    
    def _calculate_relevance_score(self, row: pd.Series, user_skills: List[str]) -> float:
        """
        Calculate relevance score based on user skills.
        
        Args:
            row: DataFrame row containing job information
            user_skills: List of user skills
            
        Returns:
            float: Relevance score (0-10)
        """
        title = str(row.get('title', '')).lower()
        description = str(row.get('description', '')).lower()
        company = str(row.get('company', '')).lower()
        
        text = f"{title} {description} {company}"
        
        # Count skill matches
        skill_matches = 0
        for skill in user_skills:
            skill_lower = skill.lower()
            if skill_lower in text:
                skill_matches += 1
        
        # Calculate base score
        base_score = (skill_matches / len(user_skills)) * 10
        
        # Bonus for exact skill matches in title
        title_bonus = 0
        for skill in user_skills:
            if skill.lower() in title:
                title_bonus += 1
        
        # Bonus for internship keywords in title
        internship_bonus = 0
        for keyword in self.internship_keywords:
            if keyword in title:
                internship_bonus += 0.5
        
        final_score = min(10.0, base_score + title_bonus + internship_bonus)
        return round(final_score, 2)

# Example usage and testing
if __name__ == "__main__":
    # Test the scraper
    scraper = InternshipScraper()
    
    test_skills = ["python", "machine learning", "data analysis"]
    test_location = "Remote"
    
    print("Testing internship scraper...")
    internships = scraper.scrape_internships(
        skills=test_skills,
        location=test_location,
        max_results=20
    )
    
    if not internships.empty:
        print(f"\nFound {len(internships)} internships:")
        print(internships[['title', 'company', 'location', 'stipend', 'relevance_score']].head())
    else:
        print("No internships found.")
