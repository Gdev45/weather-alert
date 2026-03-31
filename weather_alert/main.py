
#!/usr/bin/env python3

import requests
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

# --- COLOR MAPPING ---
def get_color(severity):
    severity = severity.lower()
    if "extreme" in severity:
        return "bold red"
    elif "severe" in severity:
        return "red"
    elif "moderate" in severity:
        return "yellow"
    elif "minor" in severity:
        return "green"
    else:
        return "cyan"


# --- USA ALERTS (NOAA API) ---
def fetch_usa_alerts():
    url = "https://api.weather.gov/alerts/active"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data["features"]
    except Exception as e:
        console.print(f"[red]Error fetching USA alerts:[/red] {e}")
        return []


# --- UK ALERTS (Met Office RSS fallback) ---
def fetch_uk_alerts():
    url = "https://www.metoffice.gov.uk/public/data/PWSCache/WarningsRSS/Region/uk"
    try:
        response = requests.get(url, timeout=10)
        return response.text
    except Exception as e:
        console.print(f"[red]Error fetching UK alerts:[/red] {e}")
        return None


# --- DISPLAY USA ALERTS ---
def display_usa(alerts):
    if not alerts:
        console.print(Panel("[green]No active alerts 🇺🇸[/green]", title="USA Weather"))
        return

    table = Table(title="🇺🇸 Active Weather Alerts", box=box.ROUNDED)

    table.add_column("Event", style="bold")
    table.add_column("Area")
    table.add_column("Severity")
    table.add_column("Headline")

    for alert in alerts[:15]:  # limit to avoid spam
        props = alert["properties"]

        event = props.get("event", "N/A")
        area = props.get("areaDesc", "N/A")
        severity = props.get("severity", "Unknown")
        headline = (props.get("headline") or "")[:60]

        color = get_color(severity)

        table.add_row(
            f"[{color}]{event}[/{color}]",
            area,
            f"[{color}]{severity}[/{color}]",
            headline
        )

    console.print(table)


# --- DISPLAY UK ALERTS (simple parse) ---
def display_uk(xml_data):
    if not xml_data:
        console.print(Panel("[green]No active alerts 🇬🇧[/green]", title="UK Weather"))
        return

    # crude parsing (kept simple)
    items = xml_data.split("<item>")[1:]

    if not items:
        console.print(Panel("[green]No active alerts 🇬🇧[/green]", title="UK Weather"))
        return

    table = Table(title="🇬🇧 UK Weather Warnings", box=box.ROUNDED)
    table.add_column("Title", style="bold magenta")
    table.add_column("Summary")

    for item in items[:10]:
        try:
            title = item.split("<title>")[1].split("</title>")[0]
            desc = item.split("<description>")[1].split("</description>")[0]

            table.add_row(title, desc[:80])
        except:
            continue

    console.print(table)


# --- MAIN UI ---
def main():
    console.print(Panel.fit(
        "[red]         WEATHER ALERTS [/red]\n"
        "Get live severe weather warnings",
        border_style="orange3"
    ))

    choice = console.input("\n[bold]Choose region ([green]UK[/green]/[blue]USA[/blue]): [/bold]").strip().lower()

    console.print("\n[dim]Fetching data...[/dim]\n")

    if choice == "usa":
        alerts = fetch_usa_alerts()
        display_usa(alerts)

    elif choice == "uk":
        xml = fetch_uk_alerts()
        display_uk(xml)

    else:
        console.print("[red]Invalid choice. Use 'UK' or 'USA'.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

def cli():
    main()
