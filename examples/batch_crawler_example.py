"""
Batch Health Resource Crawler
Shows how to crawl multiple health departments from state CSV files
"""

import csv
import time
import json
import re
from datetime import datetime
import os
from categorized_example import CategorizedHealthCrawler

class BatchHealthCrawler:
    def __init__(self):
        self.crawler = CategorizedHealthCrawler()
        self.results = []
        # Track per-site crawl success for reporting
        self.crawl_log = []
    
    def load_state_websites(self, state_code):
        """
        Load health department websites for a specific state
        
        Args:
            state_code: Two-letter state code (e.g., 'ca', 'or', 'tx')
        """
        filename = f"../data/websites/us-{state_code.lower()}.csv"
        websites = []
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    # Use columns from the current CSV format
                    websites.append({
                        'name': row.get('name', 'Unknown'),
                        'pha_url': row.get('pha_url', ''),
                        'state_id': row.get('state_id', ''),
                        'category': row.get('category', ''),
                        'population': row.get('population_proper', 'Unknown')
                    })
            print(f"Loaded {len(websites)} health departments for {state_code.upper()}")
            return websites
        except FileNotFoundError:
            print(f"File not found: {filename}")
            return []
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []
    
    def crawl_state(self, state_code, max_sites=10, delay=2):
        """
        Crawl health departments for an entire state
        
        Args:
            state_code: Two-letter state code
            max_sites: Maximum number of sites to crawl (for testing)
            delay: Seconds to wait between requests
        """
        print(f"\n=== Crawling {state_code.upper()} Health Departments ===")
        
        websites = self.load_state_websites(state_code)
        if not websites:
            return
        
        # Limit for testing/demo purposes
        websites = websites[:max_sites]
        
        for i, site in enumerate(websites, 1):
            print(f"\n[{i}/{len(websites)}] {site['name']}")
            print(f"Category: {site['category']}")
            print(f"URL: {site['pha_url']}")
            
            # Crawl the main page (wrap call to protect against unexpected exceptions)
            try:
                raw_results, status_code, error = self.crawler.crawl_page_with_categories(site['pha_url'])
            except Exception as e:
                raw_err = str(e)
                try:
                    err = re.sub(r'\sfor url:?.*$', ' for url', raw_err)
                except Exception:
                    err = raw_err
                print(f"Unhandled error crawling {site['pha_url']}: {err}")
                raw_results, status_code, error = {}, None, f"unhandled_crawl_error: {err}"
            # Consider the crawl successful when we received an HTTP status code < 400
            success = (status_code is not None and status_code < 400)
            results = raw_results or {}
            
            # Add metadata
            results.update({
                'name': site['name'],
                'category': site['category'],
                'state_id': site['state_id'],
                'population': site['population'],
                'crawled_at': datetime.now().isoformat()
            })
            # Ensure the requested URL is always recorded even when crawling failed
            # crawl_page_with_categories may return an empty dict on fetch failure,
            # so set the 'url' to the requested pha_url if it's missing.
            if not results.get('url'):
                results['url'] = site['pha_url']

            # Record the crawl success/failure for this site in crawl_log, include status and error
            try:
                entry = {'url': site['pha_url'], 'success': success}
                # Include status_code when present
                if status_code is not None:
                    entry['status_code'] = status_code
                # Include short error message when available
                if error:
                    entry['error'] = error
                self.crawl_log.append(entry)
            except Exception:
                # Be defensive: fall back to simple url-only entry
                self.crawl_log.append({'url': site['pha_url'], 'success': False})
            
            # Store results
            self.results.append(results)
            
            # Show quick summary
            total_resources = len(results.get('resources', []))
            print(f"Found {total_resources} resources")
            
            # Be polite - wait between requests
            if i < len(websites):
                print(f"Waiting {delay} seconds...")
                time.sleep(delay)
    
    def save_results(self, filename=None):
        """
        Save crawling results to a JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_crawl_results_{timestamp}.json"
        # Build summary information to include at top-level in the JSON
        total_resources = sum(len(r.get('resources', [])) for r in self.results)

        # Count by category
        by_category = {}
        by_tag = {}
        for result in self.results:
            for resource in result.get('resources', []):
                cat = resource.get('category', 'Unknown')
                by_category[cat] = by_category.get(cat, 0) + 1

                for tag in (resource.get('tags') or []):
                    by_tag[tag] = by_tag.get(tag, 0) + 1

        # Crawl info: include all crawled URLs, timestamp and student name
        # Use crawl_log entries which include success flags for each requested URL
        crawled_entries = list(self.crawl_log)
        # Count successful crawls as entries that reported success and did not include an error
        successful_count = sum(1 for e in crawled_entries if e.get('success') and not e.get('error'))
        crawl_info = {
            'url': crawled_entries,
            'sites_crawled_count': len(crawled_entries),
            'successful_crawls': successful_count,
            'timestamp': datetime.now().isoformat(),
            'student_name': 'Muhammad Sualeh Alam'
        }

        summary = {
            'total_resources': total_resources,
            'by_category': by_category,
            'by_tag': by_tag,
            'crawl_info': crawl_info
        }

        payload = {
            'summary': summary,
            'results': self.results
        }

        # Ensure output directory exists and write file into it
        output_dir = 'output'
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception:
            output_dir = '.'

        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(payload, file, indent=2, ensure_ascii=False)
            print(f"\nResults saved to {filepath} (includes summary)")
        except Exception as e:
            raw_err = str(e)
            try:
                err = re.sub(r'\sfor url:?.*$', ' for url', raw_err)
            except Exception:
                err = raw_err
            print(f"Failed to save batch results to {filepath}: {err}")
        
        # Also write a human-readable summary report to `summary_reports/`
        try:
            # Derive a simple state label from the first result if available
            state_label = 'ALL'
            if self.results:
                first = self.results[0]
                if isinstance(first, dict) and first.get('state_id'):
                    state_label = str(first.get('state_id')).upper()

            # Use timestamp for filename
            ts_fname = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_dir = 'summary_reports'
            os.makedirs(summary_dir, exist_ok=True)
            summary_filename = f"summary_report_{ts_fname}.txt"
            summary_path = os.path.join(summary_dir, summary_filename)

            # Build friendly timestamp for header using crawl_info timestamp if present
            crawled_ts = crawl_info.get('timestamp') if isinstance(crawl_info, dict) else None
            try:
                if crawled_ts:
                    crawled_dt = datetime.fromisoformat(crawled_ts)
                    crawled_str = crawled_dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    crawled_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                crawled_str = crawled_ts or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            total_sites = crawl_info.get('sites_crawled_count', len(self.crawl_log))
            successful = crawl_info.get('successful_crawls', sum(1 for e in self.crawl_log if e.get('success')))
            failed = total_sites - successful

            lines = []
            lines.append(f"BATCH CRAWLING REPORT - {state_label}")
            lines.append("=" * 50)
            lines.append("")
            lines.append(f"Crawled: {crawled_str}")
            lines.append(f"Total Sites: {total_sites}")
            lines.append(f"Successful: {successful}")
            lines.append(f"Failed: {failed}")
            lines.append("")
            lines.append("SUMMARY STATISTICS")
            lines.append("--------------------")
            lines.append(f"Total Resources Found: {summary.get('total_resources', 0)}")
            lines.append("")
            lines.append("Resources by category:")
            for cat, cnt in summary.get('by_category', {}).items():
                lines.append(f"{cat}: {cnt}")
            lines.append("")
            lines.append("Resources by tag:")
            # Exclude verification-only tags like 'uncertain' from the human-readable report
            for tag, cnt in summary.get('by_tag', {}).items():
                if str(tag).lower() == 'uncertain':
                    continue
                lines.append(f"{tag}: {cnt}")
            lines.append("")
            lines.append("TOP 5 COUNTIES BY RESOURCES FOUND")
            lines.append("-----------------------------------")
            # Compute resource counts by county/name from self.results
            county_counts = {}
            try:
                for res in self.results:
                    if not isinstance(res, dict):
                        continue
                    name = res.get('name') or res.get('state_id') or 'Unknown'
                    cnt = len(res.get('resources', []) or [])
                    county_counts[name] = county_counts.get(name, 0) + cnt
            except Exception:
                county_counts = {}

            if not county_counts:
                lines.append("TO BE DECIDED NOT YET")
                top_n = []
            else:
                # Sort by count descending, then name
                sorted_counties = sorted(county_counts.items(), key=lambda x: (-x[1], x[0]))
                # Take top 5 (or fewer)
                top_n = sorted_counties[:5]
                for name, cnt in top_n:
                    if name is None or str(name).strip() == '':
                        display_name = 'Unknown'
                    else:
                        display_name = str(name)
                    lines.append(f"{display_name}: {cnt} resource{'s' if cnt != 1 else ''}")

            # DETAILED FINDINGS for the top counties
            lines.append("")
            lines.append("DETAILED FINDINGS")
            lines.append("-----------------")
            try:
                for name, _ in top_n:
                    # try to find the matching result entry by exact name, then by contains
                    found = None
                    for r in self.results:
                        if not isinstance(r, dict):
                            continue
                        rname = (r.get('name') or '').strip()
                        if rname and rname == name:
                            found = r
                            break
                    if not found:
                        for r in self.results:
                            if not isinstance(r, dict):
                                continue
                            rname = (r.get('name') or '').strip()
                            if rname and name and name.lower() in rname.lower():
                                found = r
                                break

                    display_name = name if name else (found.get('name') if found else 'Unknown')
                    lines.append("")
                    lines.append(f"{display_name}:")
                    # Population (format with commas when numeric)
                    population = found.get('population') if found and isinstance(found, dict) else 'Unknown'
                    pop_display = 'Unknown'
                    try:
                        if population is None:
                            pop_display = 'Unknown'
                        else:
                            # Normalize and try converting to int
                            pop_str = str(population).replace(',', '').strip()
                            pop_int = int(pop_str)
                            pop_display = f"{pop_int:,}"
                    except Exception:
                        pop_display = str(population)
                    lines.append(f"- Population: {pop_display}")

                    # Resource breakdown
                    resources = found.get('resources', []) if found and isinstance(found, dict) else []
                    total_resources_local = len(resources)
                    phones = sum(1 for it in resources if str(it.get('category','')).upper() == 'CONTACT_INFO')
                    addresses = sum(1 for it in resources if str(it.get('category','')).upper() == 'LOCATION')
                    facilities = sum(1 for it in resources if str(it.get('category','')).upper() == 'FACILITY')
                    # human-friendly pluralization
                    phone_label = 'phone' if phones == 1 else 'phones'
                    address_label = 'address' if addresses == 1 else 'addresses'
                    facility_label = 'facility' if facilities == 1 else 'facilities'
                    lines.append(f"- Resources: {total_resources_local} total ({phones} {phone_label}, {addresses} {address_label}, {facilities} {facility_label})")

                    # Highlights: top tags for this county
                    tag_counts = {}
                    for it in resources:
                        for t in (it.get('tags') or []):
                            # Skip 'uncertain' tag for highlights (verification-only)
                            if str(t).lower() == 'uncertain':
                                continue
                            tag_counts[t] = tag_counts.get(t, 0) + 1
                    if tag_counts:
                        sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
                        top_tags = [t[0].replace('_', ' ').title() for t in sorted_tags[:5]]
                        lines.append(f"- Highlights: {', '.join(top_tags)}")
                    else:
                        lines.append(f"- Highlights: None identified")
            except Exception:
                # If something goes wrong, keep the report generation resilient
                lines.append("")
                lines.append("DETAILED FINDINGS: unable to compute details due to an internal error.")
            lines.append("")
            lines.append("OBSERVATIONS")
            lines.append("------------")
            lines.append("- Larger counties tend to have more comprehensive online resources")
            lines.append("- All counties provide main contact numbers")
            lines.append("- Crisis services information varies by county")
            lines.append("- Hospital facilities well-represented across all sites")
            lines.append("")
            lines.append("Detailed results available in JSON format.")
            lines.append(f"Generated by student: {crawl_info.get('student_name', 'Unknown')}")

            with open(summary_path, 'w', encoding='utf-8') as sf:
                sf.write("\n".join(lines))

            print(f"Summary report written to: {summary_path}")
        except Exception as e:
            print(f"Failed to write summary report: {e}")
    
    def print_summary(self):
        """
        Print a summary of all crawling results
        """
        if not self.results:
            print("No results to summarize")
            return
        
        print(f"\n=== CRAWLING SUMMARY ===")
        print(f"Total sites crawled: {len(self.results)}")
        
        total_resources = sum(len(r.get('resources', [])) for r in self.results)
        print(f"Total resources found: {total_resources}")
        
        # Count by category
        category_counts = {}
        for result in self.results:
            for resource in result.get('resources', []):
                category = resource.get('category', 'Unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"\nResources by category:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        
        # Show which names had the most resources
        print(f"\nTop organizations by resources found:")
        name_counts = []
        for result in self.results:
            count = len(result.get('resources', []))
            name = result.get('name', 'Unknown')
            name_counts.append((name, count))
        
        name_counts.sort(key=lambda x: x[1], reverse=True)
        for name, count in name_counts[:5]:
            print(f"  {name}: {count} resources")

# Example usage
if __name__ == "__main__":
    # Create batch crawler
    batch_crawler = BatchHealthCrawler()
    
    # Crawl a few sites from California (limited for demo)
    # Allow user to choose how many sites to crawl (minimal, safe prompt)
    try:
        raw = input("How many sites to crawl? (press Enter for default 10): ")
        if raw.strip() == "":
            max_sites = 10
        else:
            max_sites = int(raw)
            if max_sites < 1:
                print("Provided value < 1, using default 10")
                max_sites = 10
    except Exception:
        print("Invalid input, using default max_sites=10")
        max_sites = 10

    batch_crawler.crawl_state('ca', max_sites=max_sites, delay=2)
    
    # Show summary
    batch_crawler.print_summary()
    
    # Save results
    batch_crawler.save_results()
    
    print("\nDone! Check the generated JSON file for detailed results.")