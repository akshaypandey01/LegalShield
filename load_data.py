"""
Load legal cases from Hugging Face dataset.
Dataset: overthelex/indian-court-decisions (Indian Supreme Court)
License: CC-BY-4.0
"""

import os
import re
from datasets import load_dataset


def extract_case_name(text, year="", cnr=""):
    """
    Extract clean case name in "X v. Y" format from page header text.
    Strip running headers (year, month, page numbers, "SUPREME COURT REPORTS").
    
    Args:
        text: Full case text
        year: Case year if available
        cnr: CNR id as fallback
        
    Returns:
        Clean case name string
    """
    # Look in first 500 chars for case name
    header = text[:500]
    
    # Remove common running headers first
    header = re.sub(r'\d{4}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d+\.', '', header)
    header = re.sub(r'SUPREME COURT REPORTS?', '', header, flags=re.IGNORECASE)
    header = re.sub(r'S\.?C\.?R\.?', '', header, flags=re.IGNORECASE)
    header = re.sub(r'\[\d{4}\]', '', header)
    header = re.sub(r'\(\d{4}\)', '', header)
    header = re.sub(r'^\s*\d+\s+', '', header)  # Leading page numbers
    
    # Look for "X v. Y" or "X vs Y" pattern
    # Match uppercase names on both sides
    match = re.search(
        r'([A-Z][A-Za-z\s&\.,\'-]+?)\s+(?:v\.|vs\.?|V\.|Vs\.?)\s+([A-Z][A-Za-z\s&\.,\'-]+?)(?:\s|$|\.|\n)',
        header
    )
    
    if match:
        petitioner = match.group(1).strip()
        respondent = match.group(2).strip()
        
        # Clean up common noise
        petitioner = re.sub(r'\s+', ' ', petitioner).strip(' .,;:-')
        respondent = re.sub(r'\s+', ' ', respondent).strip(' .,;:-')
        
        # Cut at bracketed content or citations
        petitioner = re.split(r'[\[\(]', petitioner)[0].strip()
        respondent = re.split(r'[\[\(]', respondent)[0].strip()
        
        # Limit length
        petitioner = petitioner[:80]
        respondent = respondent[:80]
        
        case_name = f"{petitioner} v. {respondent}"
        if year:
            case_name = f"{case_name} ({year})"
        return case_name
    
    # Fallback: use CNR if available
    if cnr and cnr.strip():
        return cnr.strip()
    
    # Last resort: generic name
    return None


def is_mostly_english(text, threshold=0.9):
    """
    Check if text is mostly English (ASCII characters).
    
    Args:
        text: Text to check
        threshold: Minimum proportion of ASCII characters (default 0.9)
        
    Returns:
        True if >= threshold of characters are ASCII
    """
    if not text:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    return (ascii_chars / len(text)) >= threshold


def load_cases(n=300):
    """
    Load n Indian Supreme Court cases with filtering.
    Samples from spread across decades (year >= 1980 preferred).
    
    Args:
        n: Number of cases to load (default 300)
        
    Returns:
        List of dicts with keys: case_name, text, disposal_nature, cnr, year
    """
    print(f"Loading {n} Indian Supreme Court cases from overthelex/indian-court-decisions...")
    print("Filters: text_length >= 5000, mostly English, year >= 1980 preferred")
    
    # Load dataset in streaming mode (24 GB - never download fully)
    # Use seeded shuffle buffer to get spread across years
    dataset = load_dataset(
        "overthelex/indian-court-decisions",
        "supreme_court",
        split="train",
        streaming=True
    )
    
    # Apply shuffle with buffer for diversity
    dataset = dataset.shuffle(seed=42, buffer_size=1000)
    
    cases = []
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    seen_texts = set()  # Track duplicates
    processed = 0
    skipped_length = 0
    skipped_english = 0
    skipped_year = 0
    skipped_duplicate = 0
    
    for example in dataset:
        if len(cases) >= n:
            break
        
        processed += 1
        
        # Filter 1: text_length >= 5000
        text_length = example.get("text_length", 0)
        if text_length < 5000:
            skipped_length += 1
            continue
        
        # Get full text
        full_text = example.get("full_text", "")
        if not full_text:
            skipped_length += 1
            continue
        
        # Filter 2: Mostly English (>=90% ASCII)
        if not is_mostly_english(full_text, threshold=0.9):
            skipped_english += 1
            continue
        
        # Filter 3: Prefer year >= 1980 (but allow older if needed)
        year = example.get("year", "")
        try:
            year_int = int(year) if year else 0
            if year_int > 0 and year_int < 1980 and processed < 1500:
                # Skip very old cases early in the stream
                skipped_year += 1
                continue
        except (ValueError, TypeError):
            pass  # Non-numeric year, allow it
        
        # Filter 4: No exact duplicates
        text_hash = hash(full_text)
        if text_hash in seen_texts:
            skipped_duplicate += 1
            continue
        seen_texts.add(text_hash)
        
        # Get disposal nature
        disposal_nature = example.get("disposal_nature_normalized", "")
        if not disposal_nature or disposal_nature.strip() == "":
            disposal_nature = example.get("disposal_nature", "Not specified")
            if not disposal_nature or disposal_nature.strip() == "":
                disposal_nature = "Not specified"
        
        # Extract clean case name
        cnr = example.get("cnr", "")
        case_name = extract_case_name(full_text, year=year, cnr=cnr)
        
        # Fallback if extraction failed
        if not case_name:
            case_name = f"SC_{len(cases)+1:04d}"
            if cnr:
                case_name = cnr
            elif year:
                case_name = f"{case_name}_{year}"
        
        case_id = f"SC_{len(cases)+1:04d}"
        
        # Save to file
        case_file = os.path.join(data_dir, f"{case_id}.txt")
        with open(case_file, "w", encoding="utf-8") as f:
            f.write(f"{case_name}\n")
            f.write(full_text)
        
        cases.append({
            "case_name": case_name,
            "text": full_text,
            "disposal_nature": disposal_nature,
            "case_id": case_id,
            "cnr": cnr,
            "year": year
        })
        
        if len(cases) % 25 == 0:
            print(f"  Loaded {len(cases)}/{n} cases (processed {processed} records)...")
    
    print(f"\n✓ Successfully loaded {len(cases)} cases.")
    print(f"  Processed: {processed} records")
    print(f"  Skipped - too short: {skipped_length}")
    print(f"  Skipped - not English: {skipped_english}")
    print(f"  Skipped - old year: {skipped_year}")
    print(f"  Skipped - duplicate: {skipped_duplicate}")
    
    # Year distribution
    if cases:
        from collections import Counter
        year_counts = Counter(c.get('year', 'Unknown') for c in cases)
        print(f"\n📅 Year Distribution:")
        for year in sorted(year_counts.keys(), key=lambda x: (x == 'Unknown', x)):
            if year and str(year) != 'Unknown':
                print(f"  {year}: {year_counts[year]} cases")
        if 'Unknown' in year_counts and year_counts['Unknown'] > 0:
            print(f"  Unknown: {year_counts['Unknown']} cases")
    
    return cases

if __name__ == "__main__":
    cases = load_cases(300)
    print(f"\nTotal cases loaded: {len(cases)}")
    if cases:
        print(f"\nSample cases:")
        for i in range(min(3, len(cases))):
            print(f"  {i+1}. {cases[i]['case_name']}")
            print(f"     Disposal: {cases[i]['disposal_nature']}")
        print(f"\nFirst case preview (200 chars):")
        print(f"{cases[0]['text'][:200]}...")
