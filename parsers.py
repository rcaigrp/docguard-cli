import ast
import re
from pathlib import Path

def parse_python_code(file_path: Path) -> list:
    with open(file_path, 'r') as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    
    definitions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            definitions.append({
                'name': node.name,
                'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                'docstring': docstring,
                'line': node.lineno
            })
    return definitions

def parse_markdown_docs(file_path: Path) -> list:
    with open(file_path, 'r') as f:
        content = f.read()
    
    sections = []
    lines = content.split('\n')
    current_header = None
    current_content = []
    for line in lines:
        if line.startswith('#'):
            if current_header:
                sections.append({'title': current_header, 'content': '\n'.join(current_content).strip()})
            current_header = line.lstrip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    if current_header:
        sections.append({'title': current_header, 'content': '\n'.join(current_content).strip()})
        
    return sections
