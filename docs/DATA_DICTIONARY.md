# Data Dictionary (Crawler Output in JSON)

This document describes the JSON output produced by the batch crawler (_examples/batch_crawler_example.py_). It defines every field, the expected type, example values, and notes about privacy use.

File location (example):

- Raw output path: `examples/output/batch_crawl_results_<TIMESTAMP>.json`
- Cleaned output path: `examples/cleaned_output/batch_crawl_results_<TIMESTAMP>.cleaned.json`

Top-level JSON structure
------------------------

```
{  
  "summary": { ... },  
  "results": [ ... ]  
}  
```

Both `summary` and `results` are always present. 

* `results` is an array of per-site (county) page objects.   
* `summary` gives counts and crawl metadata.

SUMMARY OBJECT
--------------

Field: `summary` (object)
- `total_resources` (integer): Total number of resource objects across all `results` entries.
- `by_category` (object): List of category -> count Categories include `CONTACT_INFO`, `LOCATION`, `FACILITY`, `SERVICE` (string keys, integer values).
- `by_tag` (object): List of tag -> count (tags are simple strings; counts are integers). Example tags: `vaccination`, `covid19`, `pediatric`, `measles`, `vision`,  `mental_health`, `uncertain`.
- `crawl_info` (object): Metadata about the crawl run. See `CRAWL_INFO` section below.

**Example:**  
```
"summary":   
{  
  "total_resources": 46,  
  "by_category": {"CONTACT_INFO": 17, "LOCATION": 8, "SERVICE": 5, "FACILITY": 16},  
  "by_tag": {"vaccination": 7, "uncertain": 2},    
  "crawl_info": { ... }    
}  
```


CRAWL_INFO
----------

Field: `crawl_info` (object inside `summary`)
- `url` (array): Each element is an object describing a requested site crawl: 
  - `url` (string): The requested URL for that site (what was attempted).
  - `success` (boolean): True if an HTTP response was received with status < 400 (and crawl did not raise an error).
  - `status_code` (integer, optional): The HTTP status code if available (e.g., 200, 403, 402, etc).
  - `error` (string, optional): Stores a short description of error if any occurred.
- `sites_crawled_count` (integer): Total number of attempted sites crawled (contains both successful and failed attempts).
- `successful_crawls` (integer): Total count of entries deemed successful (success true and no error occurred).
- `timestamp` (string, ISO 8601): Time the summary was generated.
- `student_name` (string): Author name's string.

RESULTS ARRAY
-------------

Field: `results` (array of objects)
Each element corresponds to a single site/county crawl. 

Common fields:

- `url` (string): The page URL crawled. If fetch failed, this will still be the requested URL.
- `timestamp` (string, ISO 8601): When the page was crawled.
- `resources` (array): List of resource objects discovered on that page. See `RESOURCE OBJECT` below.
- `name` (string): Friendly site name (e.g., `Alameda County`).
- `category` (string): Site-level category (e.g., `County`).
- `state_id` (string): Two-letter state ID (e.g., `CA`).
- `population` (string or integer): Population reported in the source CSV. (The cleaning step normalizes this string to integer).
- `crawled_at` (string, ISO 8601): Timestamp, redundant with `timestamp` but kept for clarity.
- `unverified_resources` (array): Low-confidence or 'uncertain' extractions moved here. Same schema as resources.

RESOURCE OBJECT
---------------

Each resource object represents a single extracted item (phone number, address, facility name, etc.). 

Fields:

- `category` (string, required): One of the extraction categories:
  - `CONTACT_INFO` — phone numbers, and toll-free numbers.
  - `LOCATION` — postal addresses or location blocks
  - `FACILITY` — organization/facility names (clinic, health department, hospital, etc)
  - `SERVICE` — service names (e.g., "COVID-19 Vaccines", "Testing Site", "Immunization", etc)

- `type` (string, required): More specific resource type, examples:
  - `phone_number`, `toll_number`
  - `address`
  - `facility_name`
  - `service_name`

- `value` (string, required): The raw extracted text for the resource.

- Examples:
  - `"(707) 464-0861"`
  - `"1100 San Leandro Blvd. San Leandro, CA 94577"`
  - `"Alameda County Public Health Department"`

- `tags` (array[string]):  List of tags (based on keyword matching). Example: `["covid19", "vaccination"]`.
  - Note: During crawling low-confidence extractions may include the verification-only tag `uncertain`. The JSON keeps this for QA; the summary report excludes it.

- `context` (string): Rough context where the value was found (examples: `heading`, `footer`, `page`, `facility_address`, `general content`). Useful for downstream filtering.

- `confidence` (number): Float in [0, 1] expressing extractor confidence.

- Typical values used in this project:
  - `0.9` — high confidence (structured source, explicit markup, full address with street + city/state/zip)
  - `0.85` / `0.7` — medium confidence (headings, H1/H2 text, typical phone format)
  - `0.35` — very low confidence (long blobs, footer noise). Items at 0.35 are also tagged with `uncertain`.
    
- `verified` (boolean): `true` if item kept as a cleaned resource; `false` when moved to unverified_resources (or when tag 'uncertain' was present).

EXAMPLES
--------

Resource example:

```
{
  "category": "CONTACT_INFO",
  "type": "phone_number",
  "value": "(510) 267-8000",
  "tags": ["emergency_room","hiv"],
  "context": "general content",
  "confidence": 0.7,  
  "verified": true

}
```

Site result example:

```
{
  "url": "http://www.acphd.org",
  "timestamp": "2025-11-29T11:46:20.181933",
  "resources": [ ... ],
  "name": "Alameda County",
  "category": "County",
  "state_id": "CA",
  "population": "1671329",
  "crawled_at": "2025-11-29T11:46:20.339917"
}
```

CLEANING AND NORMALIZATION PROCESS
-----------------------------------

When producing the final cleaned dataset (JSON), these are the steps taken:

- Normalize population to integer: remove commas, convert to int. If missing, use `NULL` or an empty string.
- Normalize phone numbers to a single canonical format for deduplication.
- Convert `confidence` to a float column (e.g., `confidence < 0.5` treated as **FALSE POSITIVES**).  
- Normalize `tags` to a consistent set (lowercase, underscore-separated). 
- Add: `confidence_cutoff` (default): `0.5` — items with confidence < `0.5` are moved to `unverified_resources`.


PRIVACY AND ETHICS
------------------

- The crawler extracts public-facing contact information published by official county and state websites. Avoid harvesting or publishing sensitive personal data that is not publicly intended (e.g., personal email addresses in staff directories) unless you have the rights to do so.
- Respect `robots.txt`, terms of use, and rate limits. Consider adding a contact email to the user-agent if you plan repeated crawls.
- When publishing a dataset, consider whether releasing phone numbers at scale is permitted under site policies and applicable state laws.
- Before publishing, manually review _unverified_resources_ which may contain false positives.

TAG/KEYWORD NOTES
-----------------

- Tags are heuristic and derived from simple substring matching against a keyword list. They are useful for broad filtering but may include _false positives_. Use `confidence` as an additional signal.
- The `uncertain` tag is used to flag items with `confidence == 0.35` (likely false positives); it is retained in JSON for verification but is excluded from human-readable summary reports by default.
















