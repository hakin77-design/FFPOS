from sports_skills import football
import json
from datetime import datetime, timedelta
import time

print("=== Importing ALL Data from sports-skills ===\n")

all_matches = []

# 1. Get competitions
print("1. Fetching competitions...")
try:
    comps_response = football.get_competitions()
    if comps_response.get("status"):
        competitions = comps_response.get("data", [])
        print(f"   Found {len(competitions)} competitions")
        
        # Save competitions
        with open("data/sports_skills_competitions.json", "w") as f:
            json.dump(competitions, f, indent=2)
    else:
        competitions = []
        print("   No competitions found")
except Exception as e:
    print(f"   Error: {e}")
    competitions = []

# 2. Get daily schedule for last 30 days
print("\n2. Fetching historical schedules (last 30 days)...")
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

current_date = start_date
day_count = 0

while current_date <= end_date:
    try:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Note: sports-skills may not support date parameter
        # We will get today schedule and work with available data
        if day_count == 0:
            schedule = football.get_daily_schedule()
            
            if schedule.get("status"):
                data = schedule.get("data", {})
                events = data.get("events", [])
                
                print(f"   {date_str}: {len(events)} events")
                
                # Parse events
                for event in events:
                    try:
                        competitors = event.get("competitors", [])
                        if len(competitors) < 2:
                            continue
                        
                        home_team = competitors[0].get("team", {}).get("name")
                        away_team = competitors[1].get("team", {}).get("name")
                        home_score = competitors[0].get("score")
                        away_score = competitors[1].get("score")
                        
                        if not home_team or not away_team:
                            continue
                        
                        # Only include finished matches
                        if home_score is not None and away_score is not None:
                            match = {
                                "date": event.get("start_time", date_str)[:10],
                                "home_team": home_team,
                                "away_team": away_team,
                                "home_score": home_score,
                                "away_score": away_score,
                                "league": event.get("competition", {}).get("name", "Unknown"),
                                "status": event.get("status", "unknown")
                            }
                            all_matches.append(match)
                    except:
                        continue
        
        day_count += 1
        current_date += timedelta(days=1)
        
        if day_count >= 1:  # Only get today data
            break
            
    except Exception as e:
        print(f"   Error on {date_str}: {e}")
        current_date += timedelta(days=1)
        continue

print(f"\n   Total matches from schedules: {len(all_matches)}")

# 3. Try to get season data for major leagues
print("\n3. Fetching season data for major leagues...")
major_leagues = [
    ("premier-league", "Premier League"),
    ("la-liga", "La Liga"),
    ("bundesliga", "Bundesliga"),
    ("serie-a", "Serie A"),
    ("ligue-1", "Ligue 1")
]

for league_id, league_name in major_leagues:
    try:
        print(f"   {league_name}...")
        
        # Get current season
        season_response = football.get_current_season(league_id)
        if season_response.get("status"):
            season_data = season_response.get("data", {})
            season_id = season_data.get("id")
            
            if season_id:
                # Get season schedule
                schedule_response = football.get_season_schedule(season_id)
                if schedule_response.get("status"):
                    events = schedule_response.get("data", {}).get("events", [])
                    print(f"      Found {len(events)} events")
                    
                    for event in events:
                        try:
                            competitors = event.get("competitors", [])
                            if len(competitors) < 2:
                                continue
                            
                            home_team = competitors[0].get("team", {}).get("name")
                            away_team = competitors[1].get("team", {}).get("name")
                            home_score = competitors[0].get("score")
                            away_score = competitors[1].get("score")
                            
                            if not home_team or not away_team:
                                continue
                            
                            if home_score is not None and away_score is not None:
                                match = {
                                    "date": event.get("start_time", "")[:10],
                                    "home_team": home_team,
                                    "away_team": away_team,
                                    "home_score": home_score,
                                    "away_score": away_score,
                                    "league": league_name,
                                    "status": event.get("status", "unknown")
                                }
                                all_matches.append(match)
                        except:
                            continue
        
        time.sleep(1)  # Rate limiting
        
    except Exception as e:
        print(f"      Error: {e}")
        continue

print(f"\n   Total matches after season data: {len(all_matches)}")

# Remove duplicates
print("\n4. Removing duplicates...")
seen = set()
unique_matches = []

for match in all_matches:
    key = (match["date"], match["home_team"], match["away_team"], match["home_score"], match["away_score"])
    if key not in seen:
        seen.add(key)
        unique_matches.append(match)

print(f"   Unique matches: {len(unique_matches)}")

# Save all matches
with open("data/sports_skills_all_matches.json", "w") as f:
    json.dump(unique_matches, f, indent=2)

print(f"\n5. Saved to data/sports_skills_all_matches.json")

# Statistics
if unique_matches:
    leagues = set(m["league"] for m in unique_matches)
    dates = [m["date"] for m in unique_matches if m["date"]]
    
    print(f"\n=== Statistics ===")
    print(f"Total matches: {len(unique_matches)}")
    print(f"Leagues: {len(leagues)}")
    if dates:
        print(f"Date range: {min(dates)} to {max(dates)}")
    
    print(f"\nLeagues:")
    for league in sorted(leagues):
        count = sum(1 for m in unique_matches if m["league"] == league)
        print(f"  {league}: {count} matches")

print("\n✅ Data import complete!")
