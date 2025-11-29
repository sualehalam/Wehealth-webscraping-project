# Source Catalog

This source catalog lists the websites crawled for the demo run(s) and includes operational notes, basic data-quality observations, and a suggested refresh strategy. Use this to reproduce or maintain the crawl and to prioritize manual review for problem sites.

Last populated from: `examples/output/batch_crawl_results_20251129_114648.json`

## Columns:
- `name`: Friendly site name
- `url`: Canonical site URL
- `site_page`: Specific page used (if applicable)
- `type`: `county_page` / `state_portal` / `directory` / `api`
- `robots_ok`: quick robots.txt note (`yes` / `no` / `needs-review`)
- `last_checked`: timestamp when this catalog entry was validated
- `refresh_strategy`: recommended refresh schedule
- `expected_content`: typical extracted items
- `data_quality_notes`: observed issues (403, footer noise, JS-heavy, etc.)
- `contact`: public contact if available
- `example_selector`: CSS selector that often finds the contact/address block
- `status`: `active` / `blocked` / `needs-review`

---

| name | url | site_page | type | robots_ok | last_checked | refresh_strategy | expected_content | data_quality_notes | example_selector | status |
|---|---|---|---|---|---|---|---|---|---|---|
| Alameda County Public Health | http://www.acphd.org | / | county_page | needs-review | 2025-11-29T11:46:20Z | monthly | phones;addresses;services | Structured pages; headers and H1 contain service headings; low false-positive rate | `h1, .contact-info, .address` | active |
| Alpine County Health & Human Services | https://www.alpinecountyca.gov/552/Health-Human-Services | /552/Health-Human-Services | county_page | needs-review | 2025-11-29T11:46:23Z | quarterly | phones;addresses | Footer blob produced an uncertain address; requires manual review to extract canonical address  | `.footer, .contact-info` | active |
| Amador County Health & Human Services | https://www.amadorgov.org/departments/health-human-services | /departments/health-human-services | county_page | needs-review | 2025-11-29T11:46:28Z | monthly | phones;addresses | 403 Forbidden observed during crawl — blocked; consider alternate manual retrieval  | `#main, .contact` | blocked |
| Butte County Public Health | https://www.buttecounty.net/610/Public-Health | /610/Public-Health | county_page | needs-review | 2025-11-29T11:46:32Z | monthly | phones;addresses;facilities | Good structured addresses (facility_address), some footer addresses also present | `.facility_address, address` | active |
| Calaveras County Public Health | https://publichealth.calaverasgov.us/ | / | county_page | needs-review | 2025-11-29T11:46:37Z | monthly | phones;addresses;facilities | Several long heading blobs and strategic docs extracted as FACILITY entries (some uncertain) — manual QA recommended  | `h1, .heading, .contact-info` | active |
| Colusa County Public Health Division | https://www.countyofcolusa.org/99/Public-Health | /99/Public-Health | county_page | needs-review | 2025-11-29T11:46:42Z | quarterly | phones;addresses;facilities | Clean pages; footer also contains an address block captured fine  | `.contact-info, .facility_address` | active |
| Contra Costa Health Services | https://www.cchealth.org | / | county_page | needs-review | 2025-11-29T11:46:45Z | monthly | phones;addresses | 403 Forbidden observed during crawl — blocked; consider alternate manual retrieval | `#main, .contact` | blocked |
| Del Norte County Public Health | https://www.co.del-norte.ca.us/departments/publichealth | /departments/publichealth | county_page | needs-review | 2025-11-29T11:46:48Z | monthly | phones;addresses;facilities | Good phone extraction; toll-free numbers detected correctly  | `.contact-info, .address` | active |

---

### Notes & recommendations

- `robots_ok` is set to `needs-review` for many sites — please run a quick `robots.txt` check and update the catalog before large-scale automated crawls.
- For blocked sites (403), try a polite retry with a browser-like user-agent and a small delay, or record for manual data retrieval.
- For pages with long heading blobs or many PDF/strategic plan links (e.g., Calaveras), add post-processing filters (e.g., skip headings longer than 10 words, or require facility-indicator words) to reduce false positives.
- Store this catalog in version control and update `last_checked` after manual fixes or when the refresh job runs.








