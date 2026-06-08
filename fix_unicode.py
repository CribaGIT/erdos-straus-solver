import sys
with open('covering_lemma_prover.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '\u2014': '---',
    '\u2261': '=',
    '\u2264': '<=',
    '\u2208': ' in ',
    '\u00d7': 'x',
    '\u2018': "'",
    '\u2019': "'",
    '\u201c': '"',
    '\u201d': '"',
    '\u2212': '-',
    '\u2192': '->',
    '\u03c6': 'phi',
    '\u00b7': '*',
    '\u2026': '...',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('covering_lemma_prover.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('All non-ASCII characters replaced')
