import argparse
import json
import sys
from pathlib import Path
from rich.table import Table
from rich.panel import Panel

from parsers import parse_python_code, parse_markdown_docs
from drift_detector import detect_drift

def main():
    parser = argparse.ArgumentParser(description='DocGuard CLI: Detect documentation drift.')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without scanning')
    parser.add_argument('--output', help='Export findings to JSON file')
    args = parser.parse_args()
    
    if args.dry_run:
        print("Dry run mode enabled. No scanning performed.")
        return

    dir_path = Path(args.directory)
    if not dir_path.is_dir():
        print(f"Error: {dir_path} is not a directory.")
        sys.exit(1)
    
    code_defs = []
    doc_sections = []
    
    # Scan recursively
    for file in dir_path.rglob('*'):
        if file.suffix == '.py':
            code_defs.extend(parse_python_code(file))
        elif file.suffix == '.md':
            doc_sections.extend(parse_markdown_docs(file))
            
    findings = detect_drift(code_defs, doc_sections)
    
    # Output table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Element", style="blue")
    table.add_column("Type", style="green")
    table.add_column("Issue", style="red")
    table.add_column("Source", style="yellow")
    
    for f in findings:
        table.add_row(f['element'], f['type'], f['issue'], f['source'])
        
    print(Panel(table))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(findings, f, indent=2)
        print(f"Findings exported to {args.output}")

if __name__ == '__main__':
    main()
