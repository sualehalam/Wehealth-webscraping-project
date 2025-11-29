"""
Simple Health Resource Crawler
This example shows how to extract health-related information from a website.
"""

import requests
from bs4 import BeautifulSoup
import re
import time

class SimpleHealthCrawler:
    def __init__(self):
        # Set up our web session with polite headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Educational-Health-Crawler/1.0 (Learning Purpose)'
        })
    
    def get_page(self, url):
        """
        Fetch a web page and return the soup object
        """
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()  # Raises an exception for bad status codes
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def find_phone_numbers(self, text):
        """
        Find phone numbers in text using patterns
        """
        # Common phone number patterns
        patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 555-123-4567 or 555.123.4567
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',      # (555) 123-4567
        ]
        
        phone_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phone_numbers.extend(matches)
        
        # Remove duplicates and return
        return list(set(phone_numbers))
    
    def find_addresses(self, soup):
        """
        Look for addresses using common HTML patterns
        """
        addresses = []
        
        # Look for common address-related CSS classes and tags
        address_selectors = [
            '.address',
            '.location',
            '.contact-info',
            '[itemtype*="PostalAddress"]',
            'address'  # HTML address tag
        ]
        
        for selector in address_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self.looks_like_address(text):
                    addresses.append(text)
        
        return addresses
    
    def looks_like_address(self, text):
        """
        Simple check to see if text looks like an address
        """
        # Look for street indicators and numbers
        street_words = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 
                       'boulevard', 'blvd', 'drive', 'dr', 'lane', 'ln']
        
        text_lower = text.lower()
        has_number = any(char.isdigit() for char in text)
        has_street_word = any(word in text_lower for word in street_words)
        
        return has_number and has_street_word and len(text) > 10
    
    def find_clinic_names(self, soup):
        """
        Look for clinic or facility names
        """
        clinics = []
        
        # Look for headings and specific classes that might contain clinic names
        clinic_selectors = [
            'h1', 'h2', 'h3',  # Headings often contain facility names
            '.facility-name',
            '.clinic-name',
            '.location-name',
            '.facility',
            '.clinic'
        ]
        
        for selector in clinic_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self.looks_like_clinic_name(text):
                    clinics.append(text)
        
        return clinics
    
    def looks_like_clinic_name(self, text):
        """
        Check if text looks like a clinic or healthcare facility name
        """
        health_keywords = ['clinic', 'hospital', 'medical', 'health', 'center', 
                          'pharmacy', 'dental', 'care', 'urgent', 'family']
        
        text_lower = text.lower()
        has_health_keyword = any(keyword in text_lower for keyword in health_keywords)
        is_reasonable_length = 5 < len(text) < 100
        
        return has_health_keyword and is_reasonable_length
    
    def crawl_page(self, url):
        """
        Main function to crawl a page and extract all health resources
        """
        soup = self.get_page(url)
        if not soup:
            return {}
        
        # Get all the text content
        page_text = soup.get_text()
        
        # Extract different types of information
        results = {
            'url': url,
            'phone_numbers': self.find_phone_numbers(page_text),
            'addresses': self.find_addresses(soup),
            'clinic_names': self.find_clinic_names(soup)
        }
        
        return results
    
    def print_results(self, results):
        """
        Pretty print the results
        """
        print(f"\n--- Results for {results['url']} ---")
        
        print("\nPhone Numbers Found:")
        for phone in results['phone_numbers']:
            print(f"  📞 {phone}")
        
        print("\nAddresses Found:")
        for address in results['addresses']:
            print(f"  📍 {address}")
        
        print("\nClinic Names Found:")
        for clinic in results['clinic_names']:
            print(f"  🏥 {clinic}")
        
        if not any([results['phone_numbers'], results['addresses'], results['clinic_names']]):
            print("  No health resources found on this page.")

# Example usage
if __name__ == "__main__":
    # Create the crawler
    crawler = SimpleHealthCrawler()
    
    # Example: Crawl a health department page
    # Replace with a real URL you want to test
    test_url = "https://www.cdc.gov/flu/treatment/index.html"
    
    # Crawl the page
    results = crawler.crawl_page(test_url)
    
    # Show what we found
    crawler.print_results(results)
    
    # Be polite - wait before making another request
    time.sleep(1)