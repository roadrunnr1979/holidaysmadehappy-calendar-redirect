import sys
import json
import re
from datetime import datetime

def unfold(text):
    return text.replace('\r\n ', '').replace('\r\n\t', '').replace('\n ', '').replace('\n\t', '')

def parse_date(s):
    s = s.strip()
    if len(s) <= 8:
        return datetime.strptime(s, '%Y%m%d').isoformat()
    s_clean = s.rstrip('Z')
    dt = datetime.strptime(s_clean, '%Y%m%dT%H%M%S')
    return dt.isoformat() + ('Z' if s.endswith('Z') else '')

def unescape(s):
    if s is None:
        return None
    return s.replace('\\,', ',').replace('\\n', ' ').replace('\\N', ' ').replace('\\;', ';')

def parse_events(ics_text):
    text = unfold(ics_text)
    blocks = text.split('BEGIN:VEVENT')[1:]
    events = []
    for block in blocks:
        chunk = block.split('END:VEVENT')[0]
        def get(key):
            m = re.search(r'^' + key + r'(?:;[^:]*)?:(.*)$', chunk, re.MULTILINE)
            return m.group(1).strip() if m else None

        summary = get('SUMMARY')
        dtstart = get('DTSTART')
        location = get('LOCATION')
        description = get('DESCRIPTION')

        if summary and dtstart:
            events.append({
                'title': unescape(summary),
                'date': parse_date(dtstart),
                'location': unescape(location),
                'description': unescape(description)
            })
    return events

if __name__ == '__main__':
    ics_path = sys.argv[1]
    out_path = sys.argv[2]
    with open(ics_path, 'r', encoding='utf-8') as f:
        ics_text = f.read()
    events = parse_events(ics_text)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2)
