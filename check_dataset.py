from datasets import load_dataset

ds = load_dataset('overthelex/indian-court-decisions', 'supreme_court', split='train', streaming=True)

count = 0
for ex in ds:
    count += 1
    title = ex.get('title', '')
    petitioner = ex.get('petitioner', '')
    respondent = ex.get('respondent', '')
    disposal = ex.get('disposal_nature_normalized', '')
    
    if title or (petitioner and respondent):
        print(f'Case {count}:')
        print('  title:', title[:80] if title else 'None')
        print('  petitioner:', petitioner[:50] if petitioner else 'None')
        print('  respondent:', respondent[:50] if respondent else 'None')
        print('  disposal_normalized:', disposal if disposal else 'None')
        print('  disposal:', ex.get('disposal_nature', 'None'))
        print()
    
    if count >= 10:
        break
