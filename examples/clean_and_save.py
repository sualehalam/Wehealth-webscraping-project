import json
import re
from pathlib import Path


def norm_phone(val: str):
    if not val or not isinstance(val, str):
        return val
    s = val.strip()
    # Fix one common typo: missing opening parenthesis like '707) 465-0426'
    if re.match(r'^\d{3}\)\s*\d', s):
        s = '(' + s
    # Remove extension markers and common noise
    s = re.sub(r'ext\.?\s*\d+$', '', s, flags=re.I).strip()
    # Extract digits (allow leading +)
    digits = re.sub(r'[^+\d]', '', s)
    # If leading + and digits, leave as is
    if digits.startswith('+'):
        return digits
    digits = re.sub(r'\D', '', digits)
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and digits.startswith('1'):
        return f"+1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
    # fallback: return original trimmed string
    return s


def clean_doc(doc: dict, confidence_cutoff: float = 0.5):
    results = doc.get('results', []) or []
    # iterate sites
    for site in results:
        # ensure resources
        site.setdefault('resources', [])

        # unify timestamp field
        if 'timestamp' not in site and 'crawled_at' in site:
            site['timestamp'] = site.get('crawled_at')

        # normalize population to int when possible
        pop = site.get('population')
        if pop is not None and not isinstance(pop, int):
            try:
                site['population'] = int(str(pop).replace(',', '').strip())
            except Exception:
                # leave as-is when not convertible
                site['population'] = site.get('population')

        cleaned = []
        unverified = []
        seen = set()
        for r in site.get('resources', []):
            # Basic validation
            cat = r.get('category')
            typ = r.get('type')
            val = r.get('value')
            if not (cat and typ and val):
                # skip invalid entries entirely
                continue

            # normalize tags: lowercase, unique
            tags = [str(t).lower().strip() for t in (r.get('tags') or []) if str(t).strip()]
            # remove 'uncertain' from tags and set verified flag
            verified = True
            if 'uncertain' in tags:
                tags = [t for t in tags if t != 'uncertain']
                verified = False

            # dedupe tags while preserving order
            seen_tags = []
            for t in tags:
                if t not in seen_tags:
                    seen_tags.append(t)
            r['tags'] = seen_tags
            r['verified'] = verified

            # normalize whitespace on value
            r['value'] = str(val).strip()

            # normalize phones
            if 'phone' in typ or re.search(r'phone|contact', typ or '', flags=re.I) or cat == 'CONTACT_INFO':
                r['value'] = norm_phone(r['value'])

            # ensure confidence is float
            try:
                conf = float(r.get('confidence', 1.0))
            except Exception:
                conf = 0.0
            r['confidence'] = conf

            # if below cutoff -> move to unverified bucket
            if conf < confidence_cutoff or not verified:
                unverified.append(r)
                continue

            # filter out obviously long boilerplate values for entity fields
            if isinstance(r['value'], str) and len(r['value']) > 200:
                # move to unverified instead of deleting
                r['confidence'] = min(r['confidence'], 0.4)
                unverified.append(r)
                continue

            # deduplicate by (category, type, lower(value))
            key = (cat, typ, r['value'].lower())
            if key in seen:
                continue
            seen.add(key)

            cleaned.append(r)

        site['resources'] = cleaned
        if unverified:
            site['unverified_resources'] = unverified

    # Recompute summary counts from cleaned results
    by_cat = {}
    by_tag = {}
    total_resources = 0
    for site in results:
        for r in site.get('resources', []):
            total_resources += 1
            c = r.get('category', 'Unknown')
            by_cat[c] = by_cat.get(c, 0) + 1
            for t in (r.get('tags') or []):
                by_tag[t] = by_tag.get(t, 0) + 1

    # update doc.summary conservatively
    summary = doc.get('summary', {})
    summary['total_resources'] = total_resources
    summary['by_category'] = by_cat
    summary['by_tag'] = by_tag
    doc['summary'] = summary
    doc['results'] = results
    return doc


def main():
    base = Path(__file__).parent
    input_fname = None
    # Try to pick the most recent batch file in output/ if present; otherwise use known filename
    outdir = base / 'output'
    if outdir.exists():
        # find matching batch_crawl_results_*.json
        files = sorted(outdir.glob('batch_crawl_results_*.json'))
        if files:
            input_path = files[-1]
        else:
            input_path = outdir / 'batch_crawl_results_20251129_145353.json'
    else:
        input_path = base / 'output' / 'batch_crawl_results_20251129_145353.json'

    if not input_path.exists():
        print('Input file not found:', input_path)
        return

    print('Reading', input_path)
    doc = json.loads(input_path.read_text(encoding='utf-8'))

    cleaned = clean_doc(doc, confidence_cutoff=0.5)

    # ensure destination
    dest = base / 'cleaned_output'
    dest.mkdir(parents=True, exist_ok=True)
    out_name = input_path.stem + '.cleaned.json'
    out_path = dest / out_name
    out_path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Wrote cleaned file to', out_path)


if __name__ == '__main__':
    main()
