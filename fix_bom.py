#!/usr/bin/env python3
"""
Entfernt BOM (Byte Order Mark) aus pyproject.toml
"""

def fix_bom():
    with open('pyproject.toml', 'rb') as f:
        content = f.read()
    
    # Entferne BOM falls vorhanden
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
        print("BOM entfernt")
    else:
        print("Kein BOM gefunden")
    
    with open('pyproject.toml', 'wb') as f:
        f.write(content)
    
    print("pyproject.toml repariert")

if __name__ == "__main__":
    fix_bom()
