import pytest
import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, '/workspace/projects/DocGuard_CLI')

import drift_detector
import parsers
import main

@pytest.fixture
def test_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "test.py"), "w") as f:
            f.write("def foo(): pass\nclass Bar: pass")
        with open(os.path.join(tmpdir, "docs.md"), "w") as f:
            f.write("# Introduction\n# Foo")
        yield tmpdir

def test_criterion_1_scan_directory(test_dir):
    with patch('drift_detector.parse_code') as mock_code, patch('drift_detector.parse_docs') as mock_docs:
        mock_code.return_value = [{'name': 'foo', 'type': 'function'}]
        mock_docs.return_value = [{'section': 'Foo'}]
        dg = drift_detector.DocGuard(test_dir)
        assert dg.directory == test_dir

def test_criterion_2_parse_code_and_docs(test_dir):
    code = parsers.parse_code(test_dir)
    docs = parsers.parse_docs(test_dir)
    assert len(code) > 0
    assert len(docs) > 0

def test_criterion_3_identify_drift(test_dir):
    with patch('parsers.parse_code') as mock_code, patch('parsers.parse_docs') as mock_docs:
        mock_code.return_value = [{'name': 'foo', 'type': 'function'}]
        mock_docs.return_value = [{'section': 'Bar'}]
        dg = drift_detector.DocGuard(test_dir)
        findings = dg.scan()
        assert len(findings) > 0
        assert any(f['type'] == 'undocumented' for f in findings)

def test_criterion_4_rich_table(test_dir):
    with patch('rich.console.Console') as mock_console:
        with patch('main.DocGuard') as mock_dg:
            mock_dg.return_value.scan.return_value = [{'type': 'undocumented', 'element': 'foo', 'finding': 'bar'}]
            with patch('sys.argv', ['main', test_dir]):
                main.main()
            mock_console.return_value.print.assert_called()

def test_criterion_5_dry_run(test_dir):
    with patch('sys.argv', ['main', test_dir, '--dry-run']):
        with patch('main.DocGuard'):
            main.main()

def test_criterion_6_export_json(test_dir):
    with tempfile.TemporaryDirectory() as output_dir:
        output_file = os.path.join(output_dir, "output.json")
        with patch('sys.argv', ['main', test_dir, '--output', output_file]):
            with patch('main.DocGuard') as mock_dg:
                mock_dg.return_value.scan.return_value = [{'type': 'undocumented', 'element': 'foo', 'finding': 'bar'}]
                main.main()
        assert os.path.exists(output_file)