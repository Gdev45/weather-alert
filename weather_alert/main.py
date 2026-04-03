#!/usr/bin/env python3

import sys
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def pick_color(severity):
    """Return a color string based on severity."""
    severity = severity.lower()
    if "extreme" in severity:
        return "bold red"
    if "severe" in severity:
        return "red"
    if "moderate" in severity:
        return "yellow"
    if "minor" in severity:
        return "green"
    return "cyan"


def get_usa_alerts():
    """Fetch active weather alerts from NOAA (USA)."""
    try:
        resp = requests.get("https://api.weather.gov/alerts/active", timeout=10)
        return resp.json().get("features", [])
    except requests.RequestException as e:
        console.print(f"[red]Could not fetch USA alerts:[/red] {e}")
        return []


def get_uk_alerts():
    """Fetch UK weather alerts via RSS."""
    try:
        resp = requests.get(
            "https://www.metoffice.gov.uk/public/data/PWSCache/WarningsRSS/Region/uk",
            timeout=10,
        )
        return resp.text
    except requests.RequestException as e:
        console.print(f"[red]Could not fetch UK alerts:[/red] {e}")
        return ""


def show_usa(alerts):
    if not alerts:
        console.print(Panel("[green]No active alerts 🇺🇸[/green]", title="USA Weather"))
        return

    table = Table(title="🇺🇸 Active Weather Alerts", box=box.ROUNDED)
    table.add_column("Event", style="bold")
    table.add_column("Area")
    table.add_column("Severity")
    table.add_column("Headline")

    for alert in alerts[:15]:  # limit to 15 alerts
        props = alert.get("properties", {})
        event = props.get("event", "N/A")
        area = props.get("areaDesc", "N/A")
        severity = props.get("severity", "Unknown")
        headline = (props.get("headline") or "").strip()[:60]

        color = pick_color(severity)
        table.add_row(f"[{color}]{event}[/{color}]", area, f"[{color}]{severity}[/{color}]", headline)

    console.print(table)


def show_uk(rss_text):
    if not rss_text:
        console.print(Panel("[green]No active alerts 🇬🇧[/green]", title="UK Weather"))
        return

    items = rss_text.split("<item>")[1:]
    if not items:
        console.print(Panel("[green]No active alerts 🇬🇧[/green]", title="UK Weather"))
        return

    table = Table(title="🇬🇧 UK Weather Warnings", box=box.ROUNDED)
    table.add_column("Title", style="bold magenta")
    table.add_column("Summary")

    for item in items[:10]:  # limit to 10 items
        try:
            title = item.split("<title>")[1].split("</title>")[0].strip()
            desc = item.split("<description>")[1].split("</description>")[0].strip()
            table.add_row(title, desc[:80])
        except IndexError:
            continue  # skip broken items

    console.print(table)


def main():
    console.print(
        Panel.fit(
            "[red] WEATHER ALERTS [/red]\nLive severe weather warnings",
            border_style="orange3",
        )
    )

    choice = console.input("\n[bold]Region? ([green]UK[/green]/[blue]USA[/blue]): [/bold]").strip().lower()
    console.print("\n[dim]Fetching alerts...[/dim]\n")

    if choice == "usa":
        show_usa(get_usa_alerts())
    elif choice == "uk":
        show_uk(get_uk_alerts())
    else:
        console.print("[red]Invalid choice. Please enter UK or USA.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()


# alias if imported
def cli():
    main()
