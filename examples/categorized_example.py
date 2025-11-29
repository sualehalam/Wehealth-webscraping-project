"""
Categorized Health Resource Crawler
This example shows how to extract and categorize health resources with tags.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime
import os

class CategorizedHealthCrawler:
    def __init__(self):
        # self.session = requests.Session()
        # self.session.headers.update({
        #     'User-Agent': 'Educational-Health-Crawler/1.0 (Learning Purpose)'
        # })
        ### CHANGE 6: Updated session headers to mimic a real browser
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",

            ### Critical browser fingerprint headers ###
            "sec-ch-ua": '"Chromium";v="120", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",

            ### Fake but required cookie ###
            "Cookie": "CIVICPLUS=1;",
        })
        


        
        # Define health topic keywords for auto-tagging
        self.health_keywords = {
            'flu': ['flu', 'influenza', 'flu shot', 'flu vaccine'],
            'covid19': ['covid', 'covid-19', 'coronavirus', 'sars-cov-2'],
            'vaccination': ['vaccine', 'vaccination', 'immunization', 'shot'],
            'mental_health': ['mental health', 'behavioral health', 'counseling', 'therapy'],
            'pediatric': ['pediatric', 'children', 'kids', 'infant', 'child'],
            'dental': ['dental', 'dentist', 'teeth', 'oral health'],
            'emergency_room': ['emergency', 'er', 'trauma', '24 hour'],
            'urgent_care': ['urgent care', 'walk-in', 'immediate care'],
            'crisis_services': ['crisis', 'suicide', 'crisis line', 'hotline'],
            'substance_abuse': ['substance', 'addiction', 'rehab', 'detox'],
            'opioid_treatment': ['opioid', 'methadone', 'suboxone', 'narcan'],
            # Additional health keywords added by me!!!
            'rsv': ['rsv', 'respiratory syncytial', 'respiratory syncytial virus', 'respiratory syncytial virus (rsv)', 'bronchiolitis'],
            'measles': ['measles', 'rubeola', 'measles vaccine', 'mmr', 'measles immunization'],
            'tuberculosis': ['tuberculosis', 'tb', 'tb test', 'mantoux', 'tuberculin', 'latent tb', 'active tb'],
            # Mpox (monkeypox) related keywords
            'mpox': ['mpox', 'monkeypox', 'monkey pox', 'mpox vaccine', 'mpox testing', 'mpox treatment'],
            'hepatitis': ['hepatitis', 'hepatitis a', 'hepatitis b', 'hepatitis c', 'hep a', 'hep b', 'hep c', 'hepatitis vaccine', 'hepatitis testing'],
            'std': ['sexually transmitted', 'std', 'sti', 'std testing', 'sti testing', 'sexual health', 'gonorrhea', 'chlamydia', 'syphilis'],
            'vision': ['vision', 'eye care', 'optometry', 'ophthalmology', 'eye exam', 'vision screening', 'glasses'],
            # Additional approved categories
            'diabetes': ['diabetes', 'blood sugar', 'insulin', 'type 1', 'type 2', 'diabetic', 'glucometer', 'a1c'],
            'hypertension': ['hypertension', 'high blood pressure', 'bp', 'blood pressure', 'hypertensive'],
            'asthma': ['asthma', 'inhaler', 'wheezing', 'bronchospasm', 'peak flow'],
            'cancer': ['cancer', 'oncology', 'chemotherapy', 'radiation therapy', 'tumor', 'breast cancer', 'screening'],
            'hiv': ['hiv', 'human immunodeficiency virus', 'hiv testing', 'antiretroviral', 'prep', 'prep', 'post-exposure prophylaxis', 'art'],
            'maternal_health': ['maternal', 'pregnancy', 'prenatal', 'postpartum', 'obstetric', 'midwife', 'birthing'],
            'family_planning': ['contraception', 'birth control', 'family planning', 'iud', 'implant', 'condom'],
            'substance_use': ['substance use', 'opioid', 'overdose', 'naloxone', 'sober', 'detox'],
            'tobacco': ['tobacco', 'smoking', 'smoking cessation', 'quit smoking', 'nicotine replacement'],
            'nutrition': ['nutrition', 'diet', 'healthy eating', 'food security', 'nutrition counseling'],
            'physical_activity': ['exercise', 'physical activity', 'fitness', 'walking program', 'rehab'],
            'lead': ['lead', 'lead poisoning', 'lead testing', 'lead exposure', 'paint', 'child lead'],
            'vector_borne': ['mosquito', 'vector', 'tick', 'lyme', 'west nile', 'vector control'],
            'telehealth': ['telehealth', 'telemedicine', 'virtual visit', 'video visit', 'remote care'],
            # Additional suggested health-topic categories (approved)
            'palliative_care': ['palliative', 'hospice', 'end of life', 'comfort care', 'advance care planning'],
            'occupational_health': ['occupational health', 'workplace safety', 'workers compensation', 'occupational medicine'],
            'school_health': ['school nurse', 'school health', 'school-based clinic', 'student health'],
            'hearing': ['hearing', 'audiology', 'hearing aid', 'deaf', 'tinnitus', 'audiologist'],
            'dermatology': ['dermatology', 'skin', 'rash', 'eczema', 'psoriasis', 'derm clinic'],
            'kidney_disease': ['dialysis', 'kidney', 'renal', 'nephrology', 'hemodialysis', 'peritoneal dialysis'],
            'injury_trauma': ['injury', 'trauma', 'trauma center', 'fracture', 'burn', 'injury prevention'],
            'chronic_pain': ['chronic pain', 'pain management', 'pain clinic', 'analgesia', 'pain specialist'],
            'reproductive_health': ['reproductive health', 'sexual health', 'menopause', 'gynecology', 'ob-gyn'],
            'transplant_immunocompromised': ['transplant', 'immunocompromised', 'post-transplant', 'organ transplant'],
            'womens_health': ['women', "women's health", 'gynecology', 'obgyn', 'pap smear', 'mammogram', 'breast health', 'reproductive health', 'menopause'],
            'senior_care': ['senior', 'elderly', 'geriatrics', 'senior services', 'assisted living', 'home care', 'medicare', 'older adults', 'aging services']
        }
        # Service-related keywords that should produce a SERVICE category
        # Keep these lowercase; we'll do simple substring checks against text/tags.
        self.service_keywords = set([
            'vaccination', 'vaccine', 'vaccines', 'vaccination program', 'vaccination programs',
            'immunization', 'immunizations', 'immunize', 'immunization clinic', 'vaccine clinic',
            'testing', 'test', 'testing services', 'covid testing', 'test site',
            'treatment', 'treatment program', 'treatment programs', 'therapy',
            'screening', 'screenings', 'health screening', 'cancer screening',
            'mold', 'mold remediation', 'remediation', 'inspection', 'inspection request', 'request service',
            'rodent', 'rodents', 'rodent control', 'pest control',
            'food', 'food safety', 'restaurant', 'complaint', 'report a restaurant',
            'billing', 'billing assistance', 'financial assistance', 'help paying', 'hospital bill',
            'clinic', 'clinics',
            # Community support / service phrases
            'poison control', 'emergency services', 'food assistance', 'housing assistance',
            'medical transportation', 'transportation', 'language services', 'insurance help',
            'disability services', 'disability support',
            # Developmental services / early intervention
            'developmental services', 'early intervention', 'child development', 'special needs', 'early childhood services',
            # Environmental health and urgent/testing phrases
            'extreme heat', 'air quality', 'water safety', 'urgent care center', 'testing site'
        ])
        # Precompile regex patterns for service keywords using word boundaries
        # This reduces false positives for short/ambiguous terms like 'test'
        try:
            self.service_keyword_patterns = [re.compile(r"\b" + re.escape(sk) + r"\b") for sk in self.service_keywords]
        except re.error:
            # Fallback: compile a simple escaped pattern list
            self.service_keyword_patterns = [re.compile(re.escape(sk)) for sk in self.service_keywords]
        # Generic UI headings/labels to ignore as facility names
        self.generic_ui_terms = set([
            'quick links', 'categories', 'program highlights', 'contact us', 'helpful links',
            'follow us', 'sign up', 'most searched', 'connect', 'items of interest', 'resources',
            'follow us on facebook', 'follow us on social media', 'welcome',
            # Additional variants that commonly appear as non-facility headings
            'contact info', 'contact information', 'contact details', 'contact', 'contact-us',
            'site links', 'popular links', 'site map', 'sitemap', 'email public health', 'subscribe', 'newsletter',
            # Common non-facility section headings
            'our mission', 'mission', 'our commitment', 'commitment to', 'our values', 'about us', 'about', 'what we do', 'our programs', 'our services',
            # Additional UI/heading phrases to ignore (reduce false positives)
            'site footer', 'latest news', 'navigation', 'additional links', 'top menu', 'facebook', 'share this page', 'headlines', 'social media',
            'hipaa compliance', 'are you prepared for an emergency?',
        ])

        # Words that strongly indicate the text is a facility/organization
        self.facility_indicators = set([
            'department', 'public health', 'health department', 'office', 'division',
            'clinic', 'center', 'hospital', 'health services', 'healthcare'
        ])
    
    def get_page(self, url):
        """Fetch a web page and return the soup object"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup, response.status_code, None
        except requests.RequestException as e:
            # Return structured error info so callers can record status and messages
            try:
                status_code = None
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None):
                    status_code = e.response.status_code
            except Exception:
                status_code = None
            raw_err = str(e)
            # Remove the actual URL from the exception message while keeping
            # the human-readable part like '403 Client Error: Forbidden for url'
            try:
                err = re.sub(r'\sfor url:?.*$', ' for url', raw_err)
            except Exception:
                err = raw_err
            print(f"Error fetching {url}: {err}")
            return None, status_code, err
    
    def auto_tag_content(self, text, context_text=""):
        """
        Automatically assign tags based on keywords found in text and context
        """
        text_lower = (text + " " + context_text).lower()
        found_tags = []
        
        for tag, keywords in self.health_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_tags.append(tag)
        
        return found_tags
    
    def get_surrounding_context(self, element, target_text, words_around=10):
        """
        Get text context around the found element for better tagging
        """
        # Get parent element text for more context
        parent = element.parent if element.parent else element
        full_text = parent.get_text()
        
        # Find the target text and get surrounding words
        target_index = full_text.lower().find(target_text.lower())
        if target_index != -1:
            words = full_text.split()
            target_words = target_text.split()
            
            # Find approximate word position
            word_index = 0
            for i, word in enumerate(words):
                if target_words[0].lower() in word.lower():
                    word_index = i
                    break
            
            start = max(0, word_index - words_around)
            end = min(len(words), word_index + len(target_words) + words_around)
            
            return " ".join(words[start:end])
        
        return full_text[:200]  # Fallback to first 200 chars
    
    def extract_phone_with_category(self, soup):
        """
        Extract phone numbers and categorize them
        """
        results = []
        seen_values = set()
        # Use multiple phone patterns to match common formats
        phone_patterns = [
            # 1. Standard formats: 555-123-4567, 555.123.4567, 555 123 4567
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',

            # 2. With parentheses around area code: (555) 123-4567 or (555)-123-4567
            r'\(\d{3}\)\s?\d{3}[-.\s]\d{4}',

            # 3. With optional country code: +1 555-123-4567 or +1 (555) 123-4567
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ]

        # Compile a combined pattern and use finditer to get full match strings
        combined_pattern = re.compile('|'.join(f'(?:{p})' for p in phone_patterns))
        # Toll-free patterns (detect toll numbers separately)
        toll_free_patterns = [
                r'\b1?[-.\s]?\(?800\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                r'\b1?[-.\s]?\(?888\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                r'\b1?[-.\s]?\(?877\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        toll_pattern = re.compile('|'.join(f'(?:{p})' for p in toll_free_patterns))
        
        # Look for phone numbers in different contexts
        phone_contexts = [
            ('.contact-info', 'contact information'),
            ('.emergency', 'emergency services'),
            ('.crisis', 'crisis services'),
            ('.appointment', 'appointment scheduling'),
            ('body', 'general content'),
            ('.address','address'),
            ('.location','location'),
            ('.facility_address','facility address'),
            ('.service_location','service location'),
            ('.footer','footer'),
            ('.copyright','copyright information'),
            ('copyright', '.copyright information'),
            ('contact-details', 'contact details'),
            ('tel', 'telephone'),
            ('.contact-phone', 'contact phone'),
            ('.clinic-phone', 'clinic phone'),
            ('[itemtype*="ContactPoint"]', 'phone contact'),
            ('.emergency-contact', 'emergency contact'),
            ('.hotline', 'hotline')
        ]
        ### CHANGE 1: phone_contexts, added more specific selectors start from .address to .copyright
        # selectors = [
        #     '.address', '.location', '.contact-info', 'address',
        #     '.facility_address', '.service_location', '.contact',
        #     '.footer', 'footer', '.copyright'
        # ]
        
        for selector, context_type in phone_contexts:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text()
                phones = [m.group(0) for m in combined_pattern.finditer(text)]
                
                for phone in phones:
                    # Normalize by trimming whitespace
                    phone_val = phone.strip()
                    # Skip duplicates on this page
                    if phone_val in seen_values:
                        continue
                    seen_values.add(phone_val)

                    # Get surrounding context for better tagging
                    context = self.get_surrounding_context(element, phone_val)
                    tags = self.auto_tag_content(phone_val, context)
                    
                    # Determine specific category based on context
                    category = "CONTACT_INFO"
                    # Detect toll-free numbers and classify type accordingly.
                    # Use a digits-only normalization and check the area code
                    # against known toll NPAs so formats like '(800) 446-4408'
                    # are reliably detected regardless of spacing/parentheses.
                    digits_only = re.sub(r"\D", "", phone_val)
                    # If number includes leading '1' country code, area code follows
                    if digits_only.startswith('1') and len(digits_only) >= 11:
                        area_code = digits_only[1:4]
                    elif len(digits_only) >= 10:
                        area_code = digits_only[:3]
                    else:
                        area_code = ''

                    toll_npas = {'800', '888', '877', '855', '866', '844', '833', '822'}
                    is_toll = area_code in toll_npas
                    if any(tag in ['crisis_services', 'emergency_room'] for tag in tags):
                        if 'crisis' in context.lower() or 'suicide' in context.lower():
                            tags.append('crisis_hotline')
                    # Ensure we always have at least a 'general' tag when none were found
                    if not tags:
                        tags = ['general']

                    # Confidence calibration: prefer structured sources
                    is_structured_phone = False
                    try:
                        if element.name == 'a' and element.get('href', '').lower().strip().startswith('tel:'):
                            is_structured_phone = True
                    except Exception:
                        pass

                    # If selector indicates microdata or contactpoint, treat as structured
                    if '[itemtype' in selector or 'ContactPoint' in selector or context_type == 'phone contact':
                        is_structured_phone = True

                    confidence = 0.9 if is_structured_phone else 0.7

                    results.append({
                        'category': category,
                        'type': 'toll_number' if is_toll else 'phone_number',
                        'value': phone_val,
                        'tags': tags,
                        'context': context_type,
                        'confidence': confidence
                    })
        
        return results
    
    def extract_addresses_with_category(self, soup):
        """
        Extract addresses and categorize them
        """
        # Delegate to the newer, more robust address-finding logic
        return self.find_addresses(soup)

    def find_addresses(self, soup, context=""):
        """
        Extract postal addresses from HTML, including blocks that use <br> for line breaks.
        Implements the user's provided logic but uses existing helper methods
        (`looks_like_address`, `auto_tag_content`) to remain consistent.
        """
        results = []
        seen_values = set()

        # Regexes
        # Accept both 'City, ST ZIP' and 'City ST ZIP' (comma optional), case-insensitive
        city_state_zip_re = re.compile(
            r"\b([A-Z][a-zA-Z .'\-]+),?\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)\b",
            re.IGNORECASE
        )
        street_line_re = re.compile(
            r'\b\d{1,6}\s+[A-Za-z0-9\'\-.#& ]+\s+'
            r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|'
            r'Terrace|Ter|Place|Pl|Parkway|Pkwy|Highway|Hwy)\b\.?',
            re.IGNORECASE
        )

        def block_text(el):
            return el.get_text(separator="\n", strip=True)

        def merge_window(lines, idx, window=2):
            start = max(0, idx - window)
            end = min(len(lines), idx + window + 1)
            chunk = [l.strip() for l in lines[start:end] if l.strip()]
            out, seen = [], set()
            for s in chunk:
                if s not in seen:
                    seen.add(s)
                    out.append(s)
            return " ".join(out)

        def guess_address_from_block(text):
            if not text:
                return None
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            cands = [i for i, ln in enumerate(lines) if city_state_zip_re.search(ln)]
            for idx in cands:
                if street_line_re.search(lines[idx]):
                    return lines[idx]
                for j in [idx - 1, idx - 2, idx + 1, idx + 2]:
                    if 0 <= j < len(lines) and street_line_re.search(lines[j]):
                        city_part = city_state_zip_re.search(lines[idx]).group(0)
                        street_part = lines[j]
                        return f"{street_part} {city_part}".strip()
                return merge_window(lines, idx, window=2)
            for i, ln in enumerate(lines):
                if street_line_re.search(ln):
                    return merge_window(lines, i, window=2)
            return None

        # 1) Target likely containers (map selectors -> context strings)
        selectors = [
            ('.address', 'facility_address'),
            ('.location', 'service_location'),
            ('.contact-info', 'contact_info'),
            ('address', 'html_address_tag'),
            ('.facility_address', 'facility_address'),
            ('.service_location', 'service_location'),
            ('.contact', 'contact'),
            ('.footer', 'footer'),
            ('footer', 'footer'),
            ('.copyright', 'copyright')
        ]

        for sel, context_type in selectors:
            for el in soup.select(sel):
                text = block_text(el)
                candidate = guess_address_from_block(text)
                if candidate and self.looks_like_address(candidate):
                    norm = candidate.strip()
                    if norm not in seen_values:
                        seen_values.add(norm)
                        tags = self.auto_tag_content(norm, context_type)
                        if not tags:
                            tags = ['general']

                        # Confidence calibration: require both a street line and a city/state/ZIP
                        # to consider the address high-confidence (0.8). If any component
                        # is missing, use a lower base confidence (0.6). After computing
                        # the base confidence, apply the existing length-based adjustment.
                        has_street = bool(street_line_re.search(norm))
                        has_city_state_zip = bool(city_state_zip_re.search(norm))
                        base_confidence = 0.9 if (has_street and has_city_state_zip) else 0.6

                        results.append({
                            'category': 'LOCATION',
                            'type': 'address',
                            'value': norm,
                            'tags': tags,
                            'context': context_type,
                            'confidence': self._adjust_confidence_by_length(norm, base_confidence)
                        })

        # 2) Fallback: scan whole page once if nothing found yet
        if not results:
            page_text = soup.get_text(separator="\n", strip=True)
            candidate = guess_address_from_block(page_text)
            if candidate and self.looks_like_address(candidate):
                norm = candidate.strip()
                if norm not in seen_values:
                    seen_values.add(norm)
                    tags = self.auto_tag_content(norm, 'page')
                    if not tags:
                        tags = ['general']
                    # Fallback page-level inference: determine confidence based on
                    # presence of street + city/state/ZIP, then apply length adjustment.
                    has_street = bool(street_line_re.search(norm))
                    has_city_state_zip = bool(city_state_zip_re.search(norm))
                    base_confidence = 0.9 if (has_street and has_city_state_zip) else 0.6

                    results.append({
                        'category': 'LOCATION',
                        'type': 'address',
                        'value': norm,
                        'tags': tags,
                        'context': 'page',
                        'confidence': self._adjust_confidence_by_length(norm, base_confidence)
                    })

        return results
    
    def extract_facilities_with_category(self, soup):
        """
        Extract facility names and categorize them
        """
        results = []
        seen_values = set()
        
        # Look for facility names in headings and specific elements
        facility_selectors = [
            ('h1, h2, h3', 'heading'),
            ('.facility-name', 'explicit_facility'),
            ('.clinic-name', 'clinic_listing'),
            ('.location-name', 'location_listing'),
            ('h1', 'h2'),
            ('h2', 'h3')
        ]
        ### CHANGE 2: facility_selectors, added more specific selectors like .clinic-name, .location-name, and changed last two tuples from ('h1','h2') and ('h2','h3')
        
        for selector, context_type in facility_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self.looks_like_facility_name(text, context_type):
                    # Normalize and dedupe
                    name_val = text.strip()
                    # Basic cleaning: collapse whitespace
                    name_val = re.sub(r'\s+', ' ', name_val)
                    name_lower = name_val.lower()

                    # Skip obvious UI/CTA fragments or truncated text like 'I want...' or strings containing ellipses
                    if '...' in name_val or re.match(r'^(i want( to)?|want to|i want)\b', name_lower):
                        continue
                    if name_val in seen_values:
                        continue
                    seen_values.add(name_val)

                    context = self.get_surrounding_context(element, name_val)
                    tags = self.auto_tag_content(name_val, context)

                    # Add facility-specific tags
                    text_lower = text.lower()
                    if 'hospital' in text_lower:
                        tags.append('hospital')
                    elif 'clinic' in text_lower:
                        tags.append('clinic')
                    elif 'pharmacy' in text_lower:
                        tags.append('pharmacy')

                    # Ensure at least a 'general' tag when none were found
                    if not tags:
                        tags = ['general']

                    # If tags or the name text contain service-related keywords, mark this as a SERVICE
                    name_lower = name_val.lower()
                    tags_text = " ".join(tags).lower()

                    # Prefer facility when the name contains obvious facility indicators
                    has_facility_indicator = any(fi in name_lower for fi in self.facility_indicators)

                    # Exclude generic UI headings from being treated as facilities
                    is_generic_ui = any(ui in name_lower for ui in self.generic_ui_terms)

                    # Additional defensive filter: skip short generic 'contact' headings
                    # like 'Contact Info' or 'Contact Details' but do NOT skip
                    # relevant health terms like 'Contact Tracing'. We only skip
                    # when the phrase appears to be a generic UI heading.
                    if 'contact' in name_lower and 'tracing' not in name_lower:
                        words = name_lower.split()
                        if len(words) <= 3:
                            # treat as generic UI regardless of generic_ui_terms set
                            is_generic_ui = True

                    # Skip section headings that sound like mission/commitment/about
                    # These are common content headings and not facility names.
                    mission_like = ['mission', 'commitment to', 'our commitment', 'our mission', 'our values', 'about us', 'about', 'what we do']
                    if any(kw in name_lower for kw in mission_like):
                        # Skip short/medium-length mission-like headings
                        if len(name_lower.split()) <= 10:
                            is_generic_ui = True

                    # Use compiled regex patterns for robust service detection
                    def matches_service(text):
                        for pat in getattr(self, 'service_keyword_patterns', []):
                            if pat.search(text):
                                return True
                        return False

                    is_service_candidate = matches_service(tags_text) or matches_service(name_lower)

                    # A service is valid only if it's a service candidate and NOT obviously a facility
                    is_service = is_service_candidate and not has_facility_indicator and not is_generic_ui

                    # If it's generic UI text, skip adding as facility/service at all
                    if is_generic_ui:
                        continue
                    # Calibrate confidence for facility/service: explicit facility selectors and h1 get higher confidence
                    conf = 0.6
                    try:
                        if context_type == 'explicit_facility':
                            conf = 0.9
                        elif element.name == 'h1':
                            conf = 0.85
                        elif element.name in ('h2', 'h3'):
                            conf = 0.7
                    except Exception:
                        conf = 0.6

                    if is_service:
                        results.append({
                            'category': 'SERVICE',
                            'type': 'service_name',
                            'value': name_val,
                            'tags': tags,
                            'context': context_type,
                            'confidence': self._adjust_confidence_by_length(name_val, conf)
                        })
                    else:
                        # Use facility-specific confidence adjustments to catch
                        # medium-length heading blobs that are unlikely real facility names.
                        fac_conf = self._adjust_facility_confidence_by_length(name_val, conf)
                        results.append({
                            'category': 'FACILITY',
                            'type': 'facility_name',
                            'value': name_val,
                            'tags': tags,
                            'context': context_type,
                            'confidence': fac_conf
                        })
        
        return results
    
    def looks_like_address(self, text):
        """Check if text looks like an address"""
        # street_words = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 
        #                'boulevard', 'blvd', 'drive', 'dr', 'lane', 'ln']
        
        # CHANGE 3: expanded street_words list
        street_words = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 
                       'boulevard', 'blvd', 'drive', 'dr', 'lane', 'ln', 
                       'court','ct','highway','hwy','parkway','pkwy',
                       'way','place','pl','terrace','ter']
        # CHANGE 4: added is_reasonable_length check
        text_lower = text.lower()
        has_number = any(char.isdigit() for char in text)
        has_street_word = any(word in text_lower for word in street_words)
        is_reasonable_length = 10 < len(text) < 200
        
        return has_number and has_street_word and is_reasonable_length
    
    def looks_like_facility_name(self, text, context_type=None):
        """Check if text looks like a healthcare facility name.

        Exclude common non-facility headings (e.g., 'Update', 'Transcript', 'Video', 'Welcome').
        Be more permissive when the selector indicates an explicit facility or a heading.
        """
        health_keywords = ['clinic', 'hospital', 'medical', 'health', 'center',
                          'pharmacy', 'dental', 'care', 'urgent', 'family']

        exclude_terms = [
            'update', 'transcript', 'video', 'welcome', 'report', 'press',
            'notice', 'alert', 'committee', 'board', 'minutes', 'agenda'
        ]

        text_lower = text.lower()

        # Exclude obvious non-facility headings
        if any(term in text_lower for term in exclude_terms):
            return False

        has_health_keyword = any(keyword in text_lower for keyword in health_keywords)
        is_reasonable_length = 5 < len(text) < 100

        permissive_contexts = {'explicit_facility', 'clinic_listing', 'location_listing', 'heading', 'h1', 'h2', 'h3'}
        if context_type and context_type in permissive_contexts:
            # If it contains generic UI phrases, reject
            if any(ui in text_lower for ui in getattr(self, 'generic_ui_terms', [])):
                return False
            # If it has a facility indicator, accept
            if any(fi in text_lower for fi in getattr(self, 'facility_indicators', [])):
                return True
            if has_health_keyword or (is_reasonable_length and not any(p in text_lower for p in [':', 'http', 'www'])):
                return True
            return False

        return has_health_keyword and is_reasonable_length

    def _adjust_confidence_by_length(self, text, confidence):
        """Lower confidence for very long text values which are likely false-positives.

        Rules (conservative):
        - If text has more than 100 characters OR more than 12 words, reduce confidence to 0.35
        - Otherwise return original confidence
        """
        if not text:
            return confidence
        char_len = len(text)
        word_count = len(text.split())
        if char_len > 100 or word_count > 12:
            return min(confidence, 0.35)
        return confidence

    def _adjust_facility_confidence_by_length(self, text, confidence):
        """Adjust confidence for FACILITY category values with slightly different rules.

        - If text has more than 100 characters OR more than 12 words, reduce confidence to 0.35
        - If word count is greater than 7 and less than 12 (8..11 words), cap confidence at 0.55
        - Otherwise return original confidence
        """
        if not text:
            return confidence
        char_len = len(text)
        word_count = len(text.split())
        # Very long values are likely false positives
        if char_len > 100 or word_count > 12:
            return min(confidence, 0.35)
        # Mid-length facility-like strings (8-11 words) are suspicious; lower them
        if 7 < word_count < 12:
            return min(confidence, 0.55)
        return confidence
    
    def crawl_page_with_categories(self, url):
        """
        Main function to crawl a page and extract categorized resources
        """
        soup, status_code, error = self.get_page(url)
        if not soup:
            # Return an empty result along with status and error for callers to inspect
            return {}, status_code, error
        
        # Extract all categorized resources
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'resources': []
        }

        # Run each extractor with local try/except so a failure in one
        # extractor doesn't abort the whole page crawl. Collect any
        # extraction errors and return them to callers so they can log
        # or record the problem while still returning partial results.
        extraction_errors = []

        try:
            phones = self.extract_phone_with_category(soup)
            if phones:
                results['resources'].extend(phones)
        except Exception as e:
            raw_err = str(e)
            try:
                err = re.sub(r'\sfor url:?.*$', ' for url', raw_err)
            except Exception:
                err = raw_err
            print(f"Phone extraction error for {url}: {err}")
            extraction_errors.append(f"phone_extractor: {err}")

        try:
            addrs = self.extract_addresses_with_category(soup)
            if addrs:
                results['resources'].extend(addrs)
        except Exception as e:
            raw_err = str(e)
            try:
                err = re.sub(r'\sfor url:?.*$', ' for url', raw_err)
            except Exception:
                err = raw_err
            print(f"Address extraction error for {url}: {err}")
            extraction_errors.append(f"address_extractor: {err}")

        try:
            facs = self.extract_facilities_with_category(soup)
            if facs:
                results['resources'].extend(facs)
        except Exception as e:
            raw_err = str(e)
            try:
                err = re.sub(r'\sfor url:?.*$', ' for url', raw_err)
            except Exception:
                err = raw_err
            print(f"Facility extraction error for {url}: {err}")
            extraction_errors.append(f"facility_extractor: {err}")

        # Post-process: mark very low-confidence items as 'uncertain'
        try:
            for res in results.get('resources', []):
                try:
                    if float(res.get('confidence', 1.0)) == 0.35:
                        tags = res.get('tags') or []
                        if 'uncertain' not in tags:
                            tags.append('uncertain')
                            res['tags'] = tags
                except Exception:
                    # Ignore conversion problems and continue
                    continue
        except Exception:
            pass
        
        # If any extractor raised an error, return a combined sanitized
        # error string so callers (e.g. the batch crawler) can record it.
        if extraction_errors:
            combined = "; ".join(extraction_errors)
            return results, status_code, combined

        return results, status_code, None
    
    def print_categorized_results(self, results):
        """
        Pretty print categorized results
        """
        print(f"\n--- Categorized Results for {results['url']} ---")
        print(f"Crawled at: {results['timestamp']}")
        
        # Group by category
        by_category = {}
        for resource in results['resources']:
            category = resource['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(resource)
        
        for category, items in by_category.items():
            print(f"\n📋 {category} ({len(items)} items):")
            for item in items:
                tags_str = ", ".join(item['tags']) if item['tags'] else "general"
                print(f"  • {item['value']}")
                print(f"    Tags: {tags_str}")
                print(f"    Confidence: {item['confidence']}")
        
        if not results['resources']:
            print("  No categorized resources found.")
    
    def save_results(self, results, filename=None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"categorized_results_{timestamp}.json"
        # Ensure output directory exists and write file into it
        output_dir = 'output'
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception:
            # If directory creation fails for any reason, fall back to current dir
            output_dir = '.'

        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✅ Results saved to: {filepath}")
        except Exception as e:
            raw_err = str(e)
            try:
                err = re.sub(r'\sfor url:?.*$', ' for url', raw_err)
            except Exception:
                err = raw_err
            print(f"Failed to save results to {filepath}: {err}")

# Example usage
if __name__ == "__main__":
    crawler = CategorizedHealthCrawler()
    
    # Test with a health department page
    test_url = "https://www.cdc.gov/flu/treatment/index.html"
    
    results, status_code, error = crawler.crawl_page_with_categories(test_url)
    crawler.print_categorized_results(results)
    # Optionally include status/error in the saved JSON filename or content; keep current behavior
    crawler.save_results(results)