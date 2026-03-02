from sports_skills import football
import json

print("=== Integrating sports-skills ===\n")

schedule = football.get_daily_schedule()

if not schedule.get("status"):
    print(f"Error: {schedule.get(
