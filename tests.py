import unittest
import tempfile
import os
from pathlib import Path
from parsers import parse_python_code, parse_markdown_docs
from drift_detector import detect_drift

class TestParsers(unittest.TestCase):
    def test_parse_python_code(self):
        code = '''
def hello():
    """Hello world"""
    pass

class MyClass:
    """A class"""
    pass
'''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            f.flush()
            result = parse_python_code(Path(f.name))
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['name'], 'hello')
            self.assertEqual(result[1]['name'], 'MyClass')

    def test_parse_markdown_docs(self):
        md = '''
# Hello
Some text

# World
More text
'''
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as f:
            f.write(md)
            f.flush()
            result = parse_markdown_docs(Path(f.name))
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['title'], 'Hello')
            self.assertEqual(result[1]['title'], 'World')

class TestDriftDetector(unittest.TestCase):
    def test_detect_undocumented(self):
        code_defs = [{'name': 'hello', 'type': 'function', 'docstring': None}]
        doc_sections = [{'title': 'world', 'level': 1, 'content': 'text'}]
        findings = detect_drift(code_defs, doc_sections)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['issue'], 'undocumented')

if __name__ == '__main__':
    unittest.main()
