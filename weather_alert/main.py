#!/usr/bin/env python3

import requests
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()



def pick_color(level):
    level = level.lower()

    if "extreme" in level:
        return "bold red"
    if "severe" in level:
        return "red"
    if "moderate" in level:
        return "yellow"
    if "minor" in level:
        return "green"

    return "cyan"



def get_usa():
    url = "https://api.weather.gov/alerts/active"

    try:
        r = requests.get(url, timeout=10)
        return r.json().get("features", [])
    except Exception as e:
        console.print(f"[red]Failed to fetch USA alerts:[/red] {e}")
        return []



def get_uk():
    url = "https://www.metoffice.gov.uk/public/data/PWSCache/WarningsRSS/Region/uk"

    try:
        r = requests.get(url, timeout=10)
        return r.text
    except Exception as e:
        console.print(f"[red]Failed to fetch UK alerts:[/red] {e}")
        return None



def show_usa(alerts):
    if not alerts:
        console.print(Panel("[green]No active alerts 🇺🇸[/green]", title="USA Weather"))
        return

    table = Table(title="🇺🇸 Active Weather Alerts", box=box.ROUNDED)
    table.add_column("Event", style="bold")
    table.add_column("Area")
    table.add_column("Severity")
    table.add_column("Headline")

    for a in alerts[:15]:  
        props = a.get("properties", {})

        event = props.get("event", "N/A")
        area = props.get("areaDesc", "N/A")
        severity = props.get("severity", "Unknown")
        headline = (props.get("headline") or "")[:60]

        c = pick_color(severity)

        table.add_row(
            f"[{c}]{event}[/{c}]",
            area,
            f"[{c}]{severity}[/{c}]",
            headline
        )

    console.print(table)



def show_uk(xml):
    if not xml:
        console.print(Panel("[green]No active alerts 🇬🇧[/green]", title="UK Weather"))
        return

    parts = xml.split("<item>")[1:]

    if not parts:
        console.print(Panel("[green]No active alerts 🇬🇧[/green]", title="UK Weather"))
        return

    table = Table(title="🇬🇧 UK Weather Warnings", box=box.ROUNDED)
    table.add_column("Title", style="bold magenta")
    table.add_column("Summary")

    for chunk in parts[:10]:
        try:
            title = chunk.split("<title>")[1].split("</title>")[0]
            desc = chunk.split("<description>")[1].split("</description>")[0]

            table.add_row(title, desc[:80])
        except:
            
            continue

    console.print(table)


def main():
    console.print(Panel.fit(
        "[red]   WEATHER ALERTS [/red]\n"
        "Live severe weather warnings",
        border_style="orange3"
    ))

    region = console.input(
        "\n[bold]Region? ([green]UK[/green]/[blue]USA[/blue]): [/bold]"
    ).strip().lower()

    console.print("\n[dim]Fetching...[/dim]\n")

    if region == "usa":
        show_usa(get_usa())
        return

    if region == "uk":
        show_uk(get_uk())
        return

    console.print("[red]Invalid choice (use UK or USA)[/red]")
    sys.exit(1)


if __name__ == "__main__":
    main()



def cli():
    main()
