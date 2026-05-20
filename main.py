import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from drift_detector import DocGuard

def main():
    parser = argparse.ArgumentParser(description="DocGuard CLI: Detect documentation drift")
    parser.add_argument("directory", help="Directory to scan recursively")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode")
    parser.add_argument("--output", choices=["json"], default=None, help="Export findings to JSON")
    args = parser.parse_args()

    if args.dry_run:
        print("Dry-run mode enabled.")
        return

    console = Console()
    doc_guard = DocGuard(args.directory)
    findings = doc_guard.scan()

    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(findings, f)
        print(f"Findings exported to {args.output}")
    else:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Type", style="dim", width=10)
        table.add_column("Element", style="bright_cyan", width=30)
        table.add_column("Finding", style="yellow", width=50)
        for f in findings:
            table.add_row(f['type'], f['element'], f['finding'])
        console.print(table)

if __name__ == "__main__":
    main()