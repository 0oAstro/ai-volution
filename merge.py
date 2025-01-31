import json
import os
from typing import List, Dict, Any
import logging
from urllib.parse import urlparse, urljoin
from difflib import SequenceMatcher

def load_json_data(file_path: str) -> List[Dict[Any, Any]]:
    """
    Load JSON data from a file, handling potential errors.
    
    Args:
        file_path (str): Path to the JSON file
    
    Returns:
        List[Dict[Any, Any]]: Loaded data or empty list if file not found/invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {file_path}: {e}")
        return []

def is_valid_article(article: Dict[Any, Any]) -> bool:
    """
    Validate and filter out unwanted articles.
    
    Args:
        article (Dict[Any, Any]): Article dictionary to validate
    
    Returns:
        bool: True if article should be kept, False otherwise
    """
    # Common newsletter and subscription patterns
    newsletter_patterns = [
        'delivered to your inbox',
        'subscribe',
        'newsletter',
        'privacy policy',
        'terms of use',
        'unsubscribe',
        'your email',
        'read our privacy',
        'check out more',
        'sent straight to you',
    ]
    
    # Title patterns to exclude
    title_patterns = [
        'career', 'job opening', 'terms and conditions', 
        'privacy policy', 'disclaimer', 'advertisement',
        'subscribe now', 'subscription', 'newsletter',
        'about us', 'contact us', 'advertise with us',
    ]
    
    # Date-only title patterns
    date_patterns = [
        r'^\d{1,2}\s+[A-Za-z]+\s+\d{4}$',  # "15 January 2024"
        r'^[A-Za-z]+\s+\d{1,2},?\s+\d{4}$', # "January 15, 2024"
        r'^\d{1,2}/\d{1,2}/\d{2,4}$',       # "01/15/2024"
    ]

    title = article.get('title', '').lower()
    text = article.get('raw_text', '').lower()
    
    # Check for minimum content requirements
    if not all([
        article.get('title'),
        article.get('url'),
        len(article.get('raw_text', '')) > 100  # Increased minimum length
    ]):
        return False
    
    # Check for newsletter/subscription content
    if any(pattern in text for pattern in newsletter_patterns):
        return False
    
    # Check for unwanted title patterns
    if any(pattern in title for pattern in title_patterns):
        return False
    
    # Check for date-only titles using regex
    import re
    if any(re.match(pattern, title.strip()) for pattern in date_patterns):
        return False
    
    # Additional checks for title quality
    if len(title.split()) < 3:  # Title too short
        return False
    
    if title.isupper():  # ALL CAPS titles
        return False
    
    if len([c for c in title if c.isdigit()]) > len(title) / 2:  # Too many numbers
        return False
        
    return True

def normalize_url(url: str) -> str:
    """Normalize URL by removing query parameters and fragments."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def are_similar_titles(title1: str, title2: str, threshold: float = 0.85) -> bool:
    """Check if two titles are similar using sequence matcher."""
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() > threshold

def is_duplicate_article(article: Dict[Any, Any], existing_articles: List[Dict[Any, Any]]) -> bool:
    """Check if article is duplicate based on URL or similar title."""
    article_url = normalize_url(article.get('url', ''))
    article_title = article.get('title', '')
    
    for existing in existing_articles:
        # Check for URL duplicates
        if normalize_url(existing.get('url', '')) == article_url:
            return True
        
        # Check for title similarity
        if are_similar_titles(existing.get('title', ''), article_title):
            return True
            
    return False

def normalize_article(article: Dict[Any, Any]) -> Dict[Any, Any]:
    """Normalize article fields."""
    # Normalize image fields - ensure both image and top_image have same value
    image = article.get('image') or article.get('top_image')
    if image:
        article['image'] = image
        article['top_image'] = image
    else:
        article['image'] = None
        article['top_image'] = None
    
    # Normalize URL
    if article.get('url'):
        article['url'] = normalize_url(article['url'])
    
    return article

def merge_news_data(input_files: List[str], output_file: str, backup_output: str) -> None:
    """
    Merge and clean news data from multiple sources.
    
    Args:
        input_files (List[str]): List of input JSON file paths
        output_file (str): Primary output file path
        backup_output (str): Backup output file path
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s: %(message)s')
    
    # Collect and merge data
    merged_data = []
    duplicate_count = 0
    
    for file_path in input_files:
        logging.info(f"Processing {file_path}")
        data = load_json_data(file_path)
        
        for article in data:
            normalized_article = normalize_article(article)
            if is_valid_article(normalized_article):
                if not is_duplicate_article(normalized_article, merged_data):
                    merged_data.append(normalized_article)
                else:
                    duplicate_count += 1
    
    logging.info(f"Found and removed {duplicate_count} duplicate articles")
    logging.info(f"Total unique articles after cleaning: {len(merged_data)}")
        
    # Save to primary output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Data saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving to {output_file}: {e}")
    
    # Create backup
    try:
        with open(backup_output, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Backup data saved to {backup_output}")
    except Exception as e:
        logging.error(f"Error saving backup to {backup_output}: {e}")

def main():
    # List of input files
    input_files = [
        'espn_data.json', 
        'indianexpress_data.json', 
        'ndtv_data.json', 
        'techcrunch_data.json',
        'backup_output.json',
        'output.json'
    ]
    
    output_file = 'all_merged.json'
    backup_output = 'backup_all_merged.json'
    
    merge_news_data(input_files, output_file, backup_output)

if __name__ == "__main__":
    main()