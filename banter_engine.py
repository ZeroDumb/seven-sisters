import json
import random
import sys
import time

# Sassy error replies by uninvoked or confused sisters
ERROR_RESPONSES = [
    "Oh look, someone called {sister} — she isn't even dressed yet.",
    "You tried talking to {sister}? She's in a mood. Good luck.",
    "{sister}? Never heard of her. Is she even cleared for this op?",
    "Terminal sequence initiated: 3... 2... 1... 💥 Just kidding, puddin’!",
    "Error 404: {sister} not found. Probably off chasing butterflies.",
    "{sister} is unavailable. Please try yelling into a void instead.",
    "Who summons {sister} before coffee? Shame.",
    "{sister} is ghosting you. Respect her chaos."
]

USAGE_TAUNTS = [
    "Nice try, hacker. Proper usage: python banter_engine.py [Sister] [EventType]",
    "Syntax crimes detected. Try: python banter_engine.py Harley start",
    "Even the Bride follows instructions. You should too.",
    "This ain't Hogwarts, puddin’. Spell it right.",
    "You triggered absolutely nothing. Try again, slower this time."
]

def load_banter():
    with open('banter.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def speak(name, message, delay=0.5):
    print(f"\n[{name}] » {message}")
    time.sleep(delay)

def get_banter(main_sister, event_type):
    banter = load_banter()

    # Normalize the sister name regardless of case
    sister_key = next((s for s in banter if s.lower() == main_sister.lower()), None)
    if not sister_key:
        random_error = random.choice(ERROR_RESPONSES)
        print(f"\n❌ {random_error.format(sister=main_sister)}")
        return

    event_key = event_type.lower()
    valid_events = banter[sister_key].get("banter", {})
    if event_key not in valid_events:
        print(f"\n⚠️ {sister_key} has no idea what you're asking with event: '{event_type}'. Try again with less confusion.")
        return

    sisters = [s for s in banter if s != sister_key]
    main_lines = valid_events[event_key]

    for line in main_lines:
        speak(sister_key, line)

        if random.random() < 0.4:
            interjector = random.choice(sisters)
            interrupt_lines = banter.get(interjector, {}).get("banter", {}).get("interrupt", [])
            if interrupt_lines:
                comment = random.choice(interrupt_lines)
                speak(interjector, comment, delay=0.3)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\n📟 " + random.choice(USAGE_TAUNTS))
        sys.exit(1)

    sister = sys.argv[1]
    event_type = sys.argv[2]
    get_banter(sister, event_type)
