import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InternshipFilter:
    """
    A class to filter and rank internships based on various criteria.
    """
    
    def __init__(self):
        self.weights = {
            'relevance_score': 0.4,    # 40% weight on relevance
            'stipend': 0.3,            # 30% weight on stipend
            'recency': 0.2,            # 20% weight on recency
            'company_reputation': 0.1   # 10% weight on company reputation
        }
        
        # Well-known companies for reputation scoring
        self.prestigious_companies = {
            'google', 'microsoft', 'apple', 'amazon', 'meta', 'facebook',
            'netflix', 'uber', 'airbnb', 'spotify', 'twitter', 'linkedin',
            'salesforce', 'oracle', 'ibm', 'intel', 'nvidia', 'tesla',
            'spacex', 'palantir', 'stripe', 'square', 'paypal', 'visa',
            'mastercard', 'goldman sachs', 'morgan stanley', 'jpmorgan',
            'mckinsey', 'bain', 'bcg', 'deloitte', 'pwc', 'kpmg',
            'accenture', 'cognizant', 'infosys', 'tcs', 'wipro'
        }
    
    def filter_and_rank(self, 
                       internships: pd.DataFrame,
                       user_skills: List[str],
                       min_stipend: float = 0,
                       max_days_old: int = 30,
                       top_n: int = 25) -> pd.DataFrame:
        """
        Filter and rank internships based on user preferences.
        
        Args:
            internships (pd.DataFrame): Raw internship data
            user_skills (List[str]): User's skills
            min_stipend (float): Minimum stipend requirement
            max_days_old (int): Maximum age of job posting in days
            top_n (int): Number of top results to return
            
        Returns:
            pd.DataFrame: Filtered and ranked internships
        """
        if internships.empty:
            logger.warning("No internships to filter")
            return pd.DataFrame()
        
        logger.info(f"Starting to filter {len(internships)} internships")
        
        # Create a copy to avoid modifying original data
        df = internships.copy()
        
        # Apply filters
        df = self._apply_filters(df, min_stipend, max_days_old)
        
        if df.empty:
            logger.warning("No internships passed the filters")
            return pd.DataFrame()
        
        # Calculate ranking scores
        df = self._calculate_ranking_scores(df, user_skills)
        
        # Sort by final score
        df = df.sort_values('final_score', ascending=False)
        
        # Return top N results
        result = df.head(top_n)
        
        logger.info(f"Returning {len(result)} top internships")
        return result
    
    def _apply_filters(self, df: pd.DataFrame, min_stipend: float, max_days_old: int) -> pd.DataFrame:
        """
        Apply basic filters to the internship data.
        
        Args:
            df (pd.DataFrame): Internship data
            min_stipend (float): Minimum stipend requirement
            max_days_old (int): Maximum age of job posting
            
        Returns:
            pd.DataFrame: Filtered data
        """
        original_count = len(df)
        
        # Filter by minimum stipend
        if min_stipend > 0:
            df = df[df['stipend'] >= min_stipend]
            logger.info(f"After stipend filter: {len(df)} internships (removed {original_count - len(df)})")
        
        # Filter by maximum age (but keep unknown ages)
        if max_days_old < 999:  # 999 is our "unknown age" value
            # Keep internships with unknown age (999) and those within the age limit
            df = df[(df['days_old'] <= max_days_old) | (df['days_old'] == 999)]
            logger.info(f"After age filter: {len(df)} internships (removed {original_count - len(df)})")
        
        # Remove internships with missing critical information
        df = df.dropna(subset=['title', 'company', 'apply_url'])
        
        # Remove internships with empty apply URLs
        df = df[df['apply_url'].astype(str).str.strip() != '']
        
        # Remove internships with very low relevance scores (handle NaN values)
        # Lowered threshold to 0.1 to keep more internships
        df = df[df['relevance_score'].fillna(0) >= 0.1]
        
        logger.info(f"Final filtered count: {len(df)} internships")
        return df
    
    def _calculate_ranking_scores(self, df: pd.DataFrame, user_skills: List[str]) -> pd.DataFrame:
        """
        Calculate ranking scores for internships.
        
        Args:
            df (pd.DataFrame): Internship data
            user_skills (List[str]): User's skills
            
        Returns:
            pd.DataFrame: Data with ranking scores
        """
        # Normalize relevance score (0-10 scale) - handle NaN values
        df['relevance_normalized'] = df['relevance_score'].fillna(0) / 10.0
        
        # Normalize stipend (0-1 scale, assuming max $5000/month) - handle NaN values
        df['stipend'] = df['stipend'].fillna(0)
        max_stipend = df['stipend'].max()
        if max_stipend > 0:
            df['stipend_normalized'] = np.clip(df['stipend'] / max_stipend, 0, 1)
        else:
            df['stipend_normalized'] = 0
        
        # Calculate recency score (newer is better)
        df['recency_normalized'] = self._calculate_recency_score(df['days_old'])
        
        # Calculate company reputation score
        df['company_reputation_normalized'] = df['company'].apply(self._calculate_company_reputation)
        
        # Calculate final weighted score
        df['final_score'] = (
            df['relevance_normalized'] * self.weights['relevance_score'] +
            df['stipend_normalized'] * self.weights['stipend'] +
            df['recency_normalized'] * self.weights['recency'] +
            df['company_reputation_normalized'] * self.weights['company_reputation']
        )
        
        # Round final score to 2 decimal places
        df['final_score'] = df['final_score'].round(2)
        
        return df
    
    def _calculate_recency_score(self, days_old_series: pd.Series) -> pd.Series:
        """
        Calculate recency score (newer jobs get higher scores).
        
        Args:
            days_old_series (pd.Series): Series of days old values
            
        Returns:
            pd.Series: Normalized recency scores
        """
        # Handle NaN values and unknown ages (999)
        days_old_series = days_old_series.fillna(999)  # Fill NaN with 999
        days_old_series = days_old_series.replace(999, 30)  # Treat unknown as 30 days old
        
        # Calculate score: newer jobs get higher scores
        # Score = 1 for 0 days old, decreases linearly to 0 for 30+ days old
        recency_scores = np.clip(1 - (days_old_series / 30), 0, 1)
        
        return recency_scores
    
    def _calculate_company_reputation(self, company_name) -> float:
        """
        Calculate company reputation score.
        
        Args:
            company_name: Company name (str or any type)
            
        Returns:
            float: Reputation score (0-1)
        """
        # Handle NaN, None, or non-string values
        if pd.isna(company_name) or company_name is None:
            return 0.0
        
        # Convert to string and handle any type
        try:
            company_str = str(company_name).lower().strip()
        except:
            return 0.0
        
        if not company_str:
            return 0.0
        
        # Check if it's a prestigious company
        for prestigious_company in self.prestigious_companies:
            if prestigious_company in company_str:
                return 1.0
        
        # Check for startup indicators (medium reputation)
        startup_indicators = ['inc', 'llc', 'corp', 'ltd', 'startup', 'tech', 'software']
        if any(indicator in company_str for indicator in startup_indicators):
            return 0.5
        
        # Default score for unknown companies
        return 0.3
    
    def get_filtered_by_category(self, 
                                internships: pd.DataFrame,
                                category: str,
                                top_n: int = 10) -> pd.DataFrame:
        """
        Get top internships filtered by category.
        
        Args:
            internships (pd.DataFrame): Internship data
            category (str): Category to filter by ('high_stipend', 'recent', 'high_relevance', 'prestigious')
            top_n (int): Number of results to return
            
        Returns:
            pd.DataFrame: Filtered internships
        """
        if internships.empty:
            return pd.DataFrame()
        
        if category == 'high_stipend':
            return internships.nlargest(top_n, 'stipend')
        elif category == 'recent':
            return internships.nsmallest(top_n, 'days_old')
        elif category == 'high_relevance':
            return internships.nlargest(top_n, 'relevance_score')
        elif category == 'prestigious':
            prestigious = internships[internships['company_reputation_normalized'] >= 0.8]
            return prestigious.nlargest(top_n, 'final_score')
        else:
            return internships.head(top_n)
    
    def get_statistics(self, internships: pd.DataFrame) -> Dict:
        """
        Get statistics about the filtered internships.
        
        Args:
            internships (pd.DataFrame): Internship data
            
        Returns:
            Dict: Statistics dictionary
        """
        if internships.empty:
            return {}
        
        stats = {
            'total_internships': len(internships),
            'avg_stipend': internships['stipend'].mean(),
            'max_stipend': internships['stipend'].max(),
            'min_stipend': internships['stipend'].min(),
            'avg_relevance_score': internships['relevance_score'].mean(),
            'avg_days_old': internships['days_old'].mean(),
            'remote_count': len(internships[internships['location'].str.contains('Remote', case=False, na=False)]),
            'prestigious_companies': len(internships[internships['company_reputation_normalized'] >= 0.8]),
            'recent_internships': len(internships[internships['days_old'] <= 3])
        }
        
        return stats

# Example usage and testing
if __name__ == "__main__":
    # Test the filter
    filter_engine = InternshipFilter()
    
    # Create sample data for testing
    sample_data = pd.DataFrame({
        'title': ['Python Intern', 'Data Science Intern', 'Software Engineering Intern'],
        'company': ['Google', 'Startup Inc', 'Microsoft'],
        'location': ['Remote', 'New York', 'Seattle'],
        'stipend': [3000, 2000, 4000],
        'days_old': [1, 5, 2],
        'relevance_score': [8.5, 7.2, 9.1],
        'apply_url': ['http://example1.com', 'http://example2.com', 'http://example3.com'],
        'description': ['Great opportunity', 'Amazing role', 'Excellent position']
    })
    
    print("Testing internship filter...")
    filtered = filter_engine.filter_and_rank(
        internships=sample_data,
        user_skills=['python', 'data science'],
        min_stipend=1500,
        max_days_old=7,
        top_n=5
    )
    
    if not filtered.empty:
        print(f"\nFiltered {len(filtered)} internships:")
        print(filtered[['title', 'company', 'stipend', 'final_score']])
        
        stats = filter_engine.get_statistics(filtered)
        print(f"\nStatistics: {stats}")
    else:
        print("No internships passed the filters.")
