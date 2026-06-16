# IT Helpdesk Ticket Tracker — Python CLI

A command-line ticket management tool built in Python that replicates the core workflow of a real helpdesk ticketing system — logging issues, triaging by priority, tracking status, and closing tickets with documented resolutions. All data persists locally in CSV format with no external dependencies.

This project was built to reinforce my understanding of how ticketing systems like Zendesk, Freshdesk, and osTicket work under the hood — and to demonstrate that I can automate and script helpdesk workflows, not just use off-the-shelf tools.

---

## Project overview

- **Language:** Python 3.12
- **Storage:** Local CSV (no database required)
- **Platform:** Windows / PowerShell
- **Tools:** VS Code, Python standard library (`csv`, `datetime`, `os`)

---

## What this project demonstrates

- Writing a functional CLI application around a real IT workflow
- Managing persistent data with Python's `csv` module — reading, writing, and updating records across sessions
- Designing a ticket lifecycle: Open → In Progress → Resolved → Closed
- Implementing triage fields — priority levels (Low / Medium / High / Critical), categories (Hardware / Software / Network / Account / Printer / Email), and agent assignment
- Enforcing resolution documentation — tickets cannot be closed without a written resolution summary
- Building a stats dashboard that gives a live snapshot of the ticket queue by status and priority

---

## How it works

### 1. Launching the tracker

Running `ticket_tracker.py` opens the main menu with all available commands. On first run, the script automatically creates the `data/tickets.csv` file to store all ticket records.

![App Menu](01-app-menu.png)

### 2. Creating a ticket

Selecting option 1 walks through creating a new ticket — title, description, priority, category, and assignment. Each ticket gets a unique auto-generated ID (e.g. `TKT-DPYCA`) and is timestamped on creation.

![First Ticket](02-ticket-list.png)

### 3. Viewing the ticket queue

Option 2 lists all tickets in a formatted table showing ID, status, priority, category, assigned technician, and title — the same information you'd see in the queue view of any real ticketing system.

![Ticket Queue](03-ticket-list-multiple.png)

### 4. Closing a ticket with a resolution

Selecting option 5 prompts for the ticket ID and requires a written resolution summary before the status changes to Closed — enforcing documentation discipline the same way real helpdesk SLAs do.

![Ticket Closed](04-ticket-closed.png)

### 5. Stats dashboard

Option 6 displays a live breakdown of all tickets by status and priority, giving a quick overview of the current queue — similar to the dashboard view in Zendesk or Freshdesk.

![Stats Dashboard](05-stats-dashboard.png)

---

## Code breakdown

| Function | Purpose |
|---|---|
| `generate_id()` | Creates a unique ticket ID like `TKT-DPYCA` |
| `load_tickets()` | Reads all tickets from the CSV file into memory |
| `save_tickets()` | Writes the updated ticket list back to CSV |
| `cmd_new()` | Walks through creating a new ticket interactively |
| `cmd_list()` | Displays all tickets in a formatted table |
| `cmd_update()` | Updates status, priority, assignment, or adds notes |
| `cmd_close()` | Closes a ticket and requires a resolution summary |
| `cmd_stats()` | Displays a live dashboard of tickets by status and priority |

---

## Full source code

```python
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
```

---

## Key takeaways

Building this tool made the internals of ticketing systems much clearer — every field in the data model exists for a reason, and the workflow logic (triage, assignment, resolution enforcement) directly mirrors what helpdesk analysts do day to day. Combined with the [osTicket Help Desk Lab](https://github.com/Ghummun/osticket-help-desk-lab), this project shows both sides: using a production ticketing system and understanding how to build and automate one from scratch.

---

## Tools used

- Python 3.12
- VS Code
- PowerShell
- Windows 11
