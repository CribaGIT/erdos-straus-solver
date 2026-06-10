"""Fix non-ASCII chars in notebook for Kaggle CLI upload."""
import sys
FILE = sys.argv[1] if len(sys.argv) > 1 else 'erdos_kaggle_scale_prover.ipynb'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '\u2014': '---', '\u2013': '-',
    '\u2261': '=', '\u2264': '<=',
    '\u2208': ' in ', '\u00d7': 'x',
    '\u2018': "'", '\u2019': "'",
    '\u201c': '"', '\u201d': '"',
    '\u2212': '-', '\u2192': '->',
    '\u03c6': 'phi', '\u00b7': '*',
    '\u2026': '...', '\u0151': 'o',
    '\u2078': '^8', '\u2079': '^9',
    '\u2088': '_8', '\u2089': '_9',
    '\u2500': '-', '\u2502': '|',
    '\u250c': '+', '\u2510': '+',
    '\u2514': '+', '\u2518': '+',
    '\u251c': '+', '\u2524': '+',
    '\u252c': '+', '\u2534': '+',
    '\u253c': '+',
}

for old, new in replacements.items():
    content = content.replace(old, new)

content = ''.join(c if ord(c) < 128 else '?' for c in content)
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

with open(FILE, 'rb') as f:
    data = f.read()
bad = [i for i, b in enumerate(data) if b >= 0x80]
print(f'Fixed {FILE}: {len(bad)} non-ASCII bytes remaining')
assert len(bad) == 0, f'Still has non-ASCII at {bad[:10]}'
print('All ASCII - ready to push')
