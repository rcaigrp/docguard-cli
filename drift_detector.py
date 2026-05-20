def detect_drift(code_defs: list, doc_sections: list) -> list:
    findings = []
    for code in code_defs:
        matched = False
        for doc in doc_sections:
            if doc['title'].lower() == code['name'].lower():
                matched = True
                break
        if not matched:
            findings.append({
                'element': code['name'],
                'type': code['type'],
                'issue': 'undocumented',
                'source': 'code'
            })
    return findings
