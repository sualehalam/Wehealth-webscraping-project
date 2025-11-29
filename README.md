# Health Resource Crawler 

## Project Layout - Complete Project Structure
```
health-crawler/
├── README.md
├── requirements.txt
├── data/
│   ├── README.md
│   └── websites/
│       ├── us-ca.csv
│       ├── us-or.csv
│       ├── us-tx.csv
│       └── ...
├── examples/
│   ├── simple_example.py
│   ├── categorized_example.py
│   ├── batch_crawler_example.py
│   ├── clean_and_save.py
│   ├── cleaned_output/
|       ├──batch_crawl_results_20251129_145353.cleaned
|       └── ... 
│   ├── output/
│       ├── batch_crawl_results_20251129_143325.json
│       ├── batch_crawl_results_20251129_144556.json
│       ├── batch_crawl_results_20251129_145053.json
│       ├── batch_crawl_results_20251129_145353.json
|       └── ...
|   └── summary_reports/
│       ├── summary_report_20251129_143325.txt
│       ├── summary_report_20251129_1445565.json
│       ├── summary_report_20251129_145053.json
│       ├── summary_report_20251129_145353.json
|       └── ...
├── docs/
│   ├── DATA_DICTIONARY.md
│   └── SOURCE_CATALOG.md
```
## Health Resource Crawler
A beginner-friendly web crawler for extracting public health resources from websites.


## What This Does

This crawler finds:
- 📞 Phone numbers for health services
- 📍 Addresses of clinics and health facilities  
- 🏥 Names of healthcare facilities
- 🏷️ Automatically categorizes and tags each resource

## Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the Batch Crawler
```bash
python .\batch_crawler_example.py
```


## Important Considerations

- Always be respectful when crawling websites and respecting _robot.txt_
- Add delays between requests (`time.sleep(2)`)
- Some websites may block automated access
- This is for educational purposes only

## State Data

We were given CSV files with health department websites for each state:  
- California: 58 counties in `data/state_websites/us-ca.csv`
- Oregon: 36 counties in `data/state_websites/us-or.csv`
- Texas: 254 counties in `data/state_websites/us-tx.csv`

## Categories and Tags

Resources are automatically categorized:
- **CONTACT_INFO**: Phone numbers, emails
- **LOCATION**: Addresses, geographic areas
- **FACILITY**: Clinic and hospital names
- **SERVICE**: Health services offered

  And tagged by health topic:
- Vaccination, flu, COVID-19, pediatric care, dental, mental health, etc.

## Outputs:
JSON (per-run) saved to `examples/output/`  
Human-readable summary saved to `examples/summary_reports/`  
  
