import os
import re

VIEWS_DIR = 'frontend/src/views'

files = [f for f in os.listdir(VIEWS_DIR) if f.endswith('.vue')]

for f in files:
    path = os.path.join(VIEWS_DIR, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    style_match = re.search(r'<style scoped>(.*?)</style>', content, re.DOTALL)
    if style_match:
        print(f"--- {f} ---")
        # Just to check if the classes exist
        classes_found = []
        for cls in ['.page', '.box', '.brutal-btn', '.primary-btn', '.brutal-input', '.brutal-textarea', '.status-msg', '.error-msg', '.success-msg', '.section-title']:
            if cls + ' {' in style_match.group(1) or cls + '{' in style_match.group(1):
                classes_found.append(cls)
        print("Classes found:", ", ".join(classes_found))

