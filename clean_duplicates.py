import json

print('=' * 60)
print('DUPLICATE DATA CLEANER')
print('=' * 60)

# Load data
print('Loading data/data_raw_matches.json...')
with open('data/data_raw_matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f'Total matches before cleaning: {len(matches)}')

# Remove duplicates
seen = set()
unique_matches = []

for match in matches:
    # Create unique key: date + home + away + scores
    key = (
        match.get('date', ''),
        match.get('home_team', '').lower().strip(),
        match.get('away_team', '').lower().strip(),
        match.get('home_score', ''),
        match.get('away_score', '')
    )
    
    if key not in seen:
        seen.add(key)
        unique_matches.append(match)

duplicates_removed = len(matches) - len(unique_matches)
print(f'Total matches after cleaning: {len(unique_matches)}')
print(f'Duplicates removed: {duplicates_removed}')

# Save cleaned data
with open('data/data_raw_matches.json', 'w', encoding='utf-8') as f:
    json.dump(unique_matches, f, indent=2, ensure_ascii=False)

print('Cleaned data saved to data/data_raw_matches.json')
print('=' * 60)
