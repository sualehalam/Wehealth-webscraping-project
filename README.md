# Health Resource Crawler - Complete Project Structure

## Project Layout
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
│   └── sample_data/
│       └── example_page.html
├── student_template/
│   ├── README.md
│   ├── my_crawler.py
│   ├── my_batch_crawler.py
│   ├── assignment_guide.md
│   └── output/
│       ├── .gitkeep
│       └── README.md
├── reference/
│   ├── categories_and_tags.md
│   ├── extraction_patterns.md
│   └── helpful_resources.md
└── sample_outputs/
    ├── README.md
    ├── single_site_example.json
    ├── batch_crawl_example.json
    └── summary_report_example.txt
```

## Files Contents

### /README.md
```markdown
# Simple Health Resource Crawler

A beginner-friendly web crawler for extracting public health resources from websites.

## What This Does

This crawler finds:
- 📞 Phone numbers for health services
- 📍 Addresses of clinics and health facilities  
- 🏥 Names of healthcare facilities
- 🏷️ Automatically categorizes and tags each resource

## For Students

1. **Start here:** Look at `examples/simple_example.py` to see a complete working crawler
2. **Advanced example:** Check `examples/categorized_example.py` for categorization features
3. **Your assignment:** Complete the `student_template/my_crawler.py` file
4. **Get help:** Read the `student_template/assignment_guide.md`

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the simple example
python examples/simple_example.py

# Run the categorized example
python examples/categorized_example.py

# Work on your own version
cd student_template
python my_crawler.py
```

## Project Structure

- `examples/` - Complete working examples to learn from
- `student_template/` - Your assignment files to complete
- `data/` - CSV files with health department websites by state
- `reference/` - Documentation and guides
- `sample_outputs/` - Example output files

## Important Notes

- Always be respectful when crawling websites
- Add delays between requests (`time.sleep(1)`)
- Some websites may block automated access
- This is for educational purposes only

## State Data

We provide CSV files with health department websites for each state:
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

## Need Help?

Check the `reference/` folder for:
- Category and tag definitions
- Common regex patterns
- CSS selector examples
- Troubleshooting tips