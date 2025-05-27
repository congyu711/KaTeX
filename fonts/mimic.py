'''
try to mimic katex_*.ttf with firamath.otf
'''

from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from fontTools.ttLib.tables._n_a_m_e import NameRecord

def get_ttf_unicode_chars(ttf_path):
    font = TTFont(ttf_path)
    cmap = font['cmap'].getBestCmap()
    return set(cmap.keys())  # Unicode codepoints

def set_font_name(font: TTFont, new_family: str, new_subfamily: str):
    name_table = font['name']
    for record in name_table.names:
        if record.nameID == 1:  # Font Family
            record.string = new_family.encode(record.getEncoding())
        elif record.nameID == 2:  # Subfamily (e.g., Regular, Bold)
            record.string = new_subfamily.encode(record.getEncoding())
        elif record.nameID == 4:  # Full font name
            full_name = f"{new_family}-{new_subfamily}"
            record.string = full_name.encode(record.getEncoding())
        elif record.nameID == 6:  # PostScript name
            ps_name = f"{new_family}-{new_subfamily}"
            record.string = ps_name.encode(record.getEncoding())

def subset_otf(source_otf_path, unicode_codepoints, output_path, subfamily):
    font = TTFont(source_otf_path, recalcBBoxes=False, recalcTimestamp=False)
    options = Options()
    options.set(layout_features='*')  # Keep GPOS, GSUB features
    options.set(name_IDs='*')         # Keep all name records except some nameIDs, see below
    options.set(name_legacy=True)
    options.set(name_languages='*')
    options.set(glyph_names=True)
    options.set(notdef_glyph=True)
    options.set(recommended_glyphs=True)
    options.set(legacy_cmap=True)
    options.set(symbol_cmap=True)
    options.set(prune_unicode_ranges=False)
    options.set(drop_tables=[])       # Don't drop any tables, including MATH
    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=unicode_codepoints)
    subsetter.subset(font)
    set_font_name(font, output_path.split("-")[0], subfamily)
    font.save(output_path)


# helper functions for tests
def print_charset(font_path):
    unicode_chars=get_ttf_unicode_chars(font_path)
    for codepoint in sorted(unicode_chars):
        char = chr(codepoint)
        print(f"U+{codepoint:04X} {char}")

def print_font_names(font_path):
    font = TTFont(font_path)
    for record in font['name'].names:
        try:
            decoded = record.string.decode(record.getEncoding())
        except UnicodeDecodeError:
            decoded = record.string.decode('utf-8', errors='replace')
        print(f"NameID {record.nameID:2d}: {decoded} (PlatformID={record.platformID}, LangID={record.langID})")

# generate font
def createsubset(katex_font_path, firamath_font_path):
    font_style = katex_font_path.split(".")[0].split("-")[-1]
    O_name="FiraMath_"+katex_font_path.split(".")[0].split("_")[-1]+".otf"
    subset_otf(firamath_font_path, get_ttf_unicode_chars(katex_font_path), O_name, font_style)

# NO..... i have to do this manually since they are mapping things in a weird way! 
# KaTeX_AMS font is mapping Latin Capital Letter to blackboard A... I do not see the point of this...
fontlist=[
    ("KaTeX_AMS-Regular.ttf","FiraMath-AMS-Regular.otf"),
    # ("KaTeX_Main-Bold.ttf","FiraMath-Regular.otf"),
    # ("KaTeX_Main-BoldItalic.ttf","FiraMath-Regular.otf"),
    ("KaTeX_Main-Italic.ttf","FiraMath-Italic.otf"),
    ("KaTeX_Main-Regular.ttf","FiraMath-Regular.otf"),
    ("KaTeX_Math-Italic.ttf","FiraMath-Italic.otf"),
    ("KaTeX_Size1-Regular.ttf","FiraMath-SIZEONE.otf"),
    ("KaTeX_Size2-Regular.ttf","FiraMath-SIZETWO.otf"),
    ("KaTeX_Size3-Regular.ttf","FiraMath-SIZETHREE.otf"),
    ("KaTeX_Size4-Regular.ttf","FiraMath-SIZEFOUR.otf"),
]

# createsubset("KaTeX_AMS-Regular.ttf","FiraMath-Regular.otf")
# print_charset("KaTeX_AMS-Regular.ttf")
# print_font_names("FiraMath_AMS-Regular.otf")
# print_font_names("FiraMath-Regular.otf")

for (katex,fira) in fontlist:
    createsubset(katex,fira)
    print(f"Subsetted {fira} to {katex}")
