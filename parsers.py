import ast
import re
from pathlib import Path

def parse_code(directory: str) -> list[dict]:
    code_elements = []
    for file in Path(directory).rglob('*.py'):
        try:
            with open(file, 'r') as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    code_elements.append({'type': 'function', 'name': node.name, 'file': str(file), 'line': node.lineno})
                elif isinstance(node, ast.ClassDef):
                    code_elements.append({'type': 'class', 'name': node.name, 'file': str(file), 'line': node.lineno})
        except Exception as e:
            print(f"Error parsing {file}: {e}")
    return code_elements

def parse_docs(directory: str) -> list[dict]:
    doc_sections = []
    for file in Path(directory).rglob('*.md'):
        try:
            with open(file, 'r') as f:
                content = f.read()
            headers = re.findall(r'^# (.*?)$', content, re.MULTILINE)
            for h in headers:
                doc_sections.append({'section': h, 'file': str(file)})
        except Exception as e:
            print(f"Error parsing {file}: {e}")
    return doc_sections