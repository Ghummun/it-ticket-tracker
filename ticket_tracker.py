"""
IT Ticket Tracker
-----------------
A command-line helpdesk ticket management tool.
Logs, updates, and closes support tickets stored in a local CSV file.
"""

import csv
import os
import sys
import random
import string
from datetime import datetime

DATA_FILE = "data/tickets.csv"
FIELDNAMES = ["ticket_id", "created_at", "updated_at", "status", "priority", "category", "title", "description", "assigned_to", "resolution"]

STATUSES   = ["Open", "In Progress", "Resolved", "Closed"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
CATEGORIES = ["Hardware", "Software", "Network", "Account", "Printer", "Email", "Other"]

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def generate_id():
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"TKT-{suffix}"

def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def load_tickets():
    ensure_data_file()
    with open(DATA_FILE, newline="") as f:
        return list(csv.DictReader(f))

def save_tickets(tickets):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(tickets)

def pick_from(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  Invalid choice. Try again.")

def cmd_new():
    print("\n=== New Ticket ===")
    title = input("Title (brief summary): ").strip()
    if not title:
        print("Title cannot be empty."); return
    desc     = input("Description: ").strip()
    priority = pick_from("Priority:", PRIORITIES)
    category = pick_from("Category:", CATEGORIES)
    assigned = input("Assign to (name or leave blank): ").strip() or "Unassigned"
    ticket = {
        "ticket_id": generate_id(), "created_at": now(), "updated_at": now(),
        "status": "Open", "priority": priority, "category": category,
        "title": title, "description": desc, "assigned_to": assigned, "resolution": "",
    }
    tickets = load_tickets()
    tickets.append(ticket)
    save_tickets(tickets)
    print(f"\nTicket created: {ticket['ticket_id']}")

def cmd_list():
    tickets = load_tickets()
    if not tickets:
        print("\nNo tickets found."); return
    print(f"\n{'ID':<12} {'Status':<14} {'Priority':<10} {'Category':<12} {'Assigned':<16} Title")
    print("─" * 90)
    for t in tickets:
        print(f"{t['ticket_id']:<12} {t['status']:<14} {t['priority']:<10} {t['category']:<12} {t['assigned_to']:<16} {t['title'][:40]}")
    print(f"\n{len(tickets)} ticket(s).")

def cmd_view():
    tickets = load_tickets()
    ticket_id = input("Ticket ID: ").strip().upper()
    match = next((t for t in tickets if t["ticket_id"] == ticket_id), None)
    if not match:
        print(f"Ticket {ticket_id} not found."); return
    print(f"\n{'─'*50}")
    print(f"  {match['ticket_id']} — {match['title']}")
    print(f"{'─'*50}")
    print(f"  Status    : {match['status']}")
    print(f"  Priority  : {match['priority']}")
    print(f"  Category  : {match['category']}")
    print(f"  Assigned  : {match['assigned_to']}")
    print(f"  Created   : {match['created_at']}")
    print(f"  Updated   : {match['updated_at']}")
    print(f"\n  Description:\n  {match['description']}")
    if match["resolution"]:
        print(f"\n  Resolution:\n  {match['resolution']}")
    print(f"{'─'*50}\n")

def cmd_update():
    tickets = load_tickets()
    ticket_id = input("Ticket ID to update: ").strip().upper()
    idx = next((i for i, t in enumerate(tickets) if t["ticket_id"] == ticket_id), None)
    if idx is None:
        print(f"Ticket {ticket_id} not found."); return
    t = tickets[idx]
    print(f"\nUpdating {ticket_id}: {t['title']}")
    new_status   = pick_from(f"Status [{t['status']}]:", STATUSES)
    new_priority = pick_from(f"Priority [{t['priority']}]:", PRIORITIES)
    new_assigned = input(f"Assigned to [{t['assigned_to']}]: ").strip() or t["assigned_to"]
    new_notes    = input("Add note / resolution detail: ").strip()
    tickets[idx]["status"]      = new_status
    tickets[idx]["priority"]    = new_priority
    tickets[idx]["assigned_to"] = new_assigned
    tickets[idx]["updated_at"]  = now()
    if new_notes:
        existing = tickets[idx]["resolution"]
        tickets[idx]["resolution"] = f"{existing}; {now()}: {new_notes}".lstrip("; ")
    save_tickets(tickets)
    print(f"\nTicket {ticket_id} updated.")

def cmd_close():
    tickets = load_tickets()
    ticket_id = input("Ticket ID to close: ").strip().upper()
    idx = next((i for i, t in enumerate(tickets) if t["ticket_id"] == ticket_id), None)
    if idx is None:
        print(f"Ticket {ticket_id} not found."); return
    resolution = input("Resolution summary (required): ").strip()
    if not resolution:
        print("A resolution summary is required."); return
    tickets[idx]["status"]     = "Closed"
    tickets[idx]["resolution"] = resolution
    tickets[idx]["updated_at"] = now()
    save_tickets(tickets)
    print(f"\nTicket {ticket_id} closed.")

def cmd_stats():
    tickets = load_tickets()
    if not tickets:
        print("\nNo tickets yet."); return
    by_status   = {s: 0 for s in STATUSES}
    by_priority = {p: 0 for p in PRIORITIES}
    for t in tickets:
        by_status[t["status"]]     = by_status.get(t["status"], 0) + 1
        by_priority[t["priority"]] = by_priority.get(t["priority"], 0) + 1
    print(f"\n=== Ticket Dashboard ===\n  Total: {len(tickets)}\n")
    print("  By Status:")
    for s, count in by_status.items():
        print(f"    {s:<14} {'█' * count} {count}")
    print("\n  By Priority:")
    for p, count in by_priority.items():
        print(f"    {p:<10} {'█' * count} {count}")

MENU = {
    "1": ("New ticket",       cmd_new),
    "2": ("List all tickets", cmd_list),
    "3": ("View ticket",      cmd_view),
    "4": ("Update ticket",    cmd_update),
    "5": ("Close ticket",     cmd_close),
    "6": ("Stats dashboard",  cmd_stats),
    "0": ("Exit",             sys.exit),
}

def main():
    ensure_data_file()
    print("\n╔══════════════════════════════╗")
    print("║   IT Helpdesk Ticket Tracker  ║")
    print("╚══════════════════════════════╝")
    while True:
        print("\n── Main Menu ──────────────────")
        for key, (label, _) in MENU.items():
            print(f"  {key}. {label}")
        choice = input("\nChoice: ").strip()
        if choice in MENU:
            MENU[choice][1]()
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()