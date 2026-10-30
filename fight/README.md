# The fight

The top of the profile README looks like plain text. It isn't. `fight-light.svg` and
`fight-dark.svg` are 31-second animated SVGs (pure SMIL, no JavaScript) that GitHub renders
as-is. `make_fight.py` generates both. From the repository root:

```
python -m pip install pillow
python fight/make_fight.py
python -m unittest discover -s fight -p "test_*.py"
```

Every word is its own `<text>` with a fixed `textLength`, so the fight can kick, slice and
stand on individual words. Generation uses Liberation Sans on Linux or Arial on
Windows, and the SVG stores the measured word widths.

Edit `H1_TEXT` and `PARAS` near the top to change the introduction. The animation
targets specific words: `called` and `Bug.` on the last line, plus `teddy`,
`Engineer`, and `README,` on their current lines. If you rename those words,
update the matching `word(...)` lookups too. Keep four lines within the 830px canvas.
