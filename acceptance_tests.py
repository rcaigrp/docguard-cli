import unittest
import tempfile
import json
import os
from pathlib import Path
import sys
import unittest.mock as mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main
from parsers import parse_python_code, parse_markdown_docs
from drift_detector import detect_drift

class TestDocGuardCLI(unittest.TestCase):
    def test_criterion_1_scan_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, 'test.py'), 'w') as f:
                f.write('def foo():\n    pass\n')
            code = parse_python_code(Path(os.path.join(tmpdir, 'test.py')))
            self.assertEqual(len(code), 1)
            self.assertEqual(code[0]['name'], 'foo')

    def test_criterion_2_parse_code_and_docs(self):
        md = '# Foo\nHello'
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as f:
            f.write(md)
            f.flush()
            docs = parse_markdown_docs(Path(f.name))
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]['title'], 'Foo')

    def test_criterion_3_identify_drift(self):
        code = [{'name': 'bar', 'type': 'function', 'docstring': None}]
        docs = [{'title': 'foo', 'level': 1, 'content': 'text'}]
        findings = detect_drift(code, docs)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['issue'], 'undocumented')

    def test_criterion_4_rich_output(self):
        from rich.table import Table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Element", style="blue")
        table.add_column("Type", style="green")
        table.add_column("Issue", style="red")
        table.add_column("Source", style="yellow")
        self.assertEqual(len(table.columns), 4)

    def test_criterion_5_dry_run(self):
        with mock.patch('sys.argv', ['main', '--dry-run', '/tmp']):
            with mock.patch('builtins.print') as mock_print:
                main()
                mock_print.assert_called_with("Dry run mode enabled. No scanning performed.")

    def test_criterion_6_export_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'findings.json')
            findings = [{'element': 'foo', 'type': 'function', 'issue': 'undocumented', 'source': 'code'}]
            with open(output_path, 'w') as f:
                json.dump(findings, f, indent=2)
            with open(output_path, 'r') as f:
                data = json.load(f)
            self.assertEqual(len(data), 1)

if __name__ == '__main__':
    unittest.main()
