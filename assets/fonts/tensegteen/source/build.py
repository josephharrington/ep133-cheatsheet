# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fonttools[woff]>=4.60,<5",
# ]
# ///

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools.agl import UV2AGL
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parent
SOURCE_SVG = ROOT / "segments.svg"
MAPPING_JSON = ROOT / "mapping.json"
OUTPUT_DIR = ROOT.parent
TTF_PATH = OUTPUT_DIR / "TenSegTeen-Regular.ttf"
WOFF2_PATH = OUTPUT_DIR / "TenSegTeen-Regular.woff2"

UPM = 1000
SEGMENT_HEIGHT = 990
SEGMENT_IDS = (
    "segment-top",
    "segment-upper-left",
    "segment-upper-center",
    "segment-upper-right",
    "segment-outer-left",
    "segment-outer-right",
    "segment-lower-left",
    "segment-lower-center",
    "segment-lower-right",
    "segment-bottom",
)
DOT_ID = "decimal-point"
ZERO_ADVANCE_PUNCTUATION = {".", ","}
SCAFFOLD_ALIASES = {0x00A1: "uniE000", 0x2122: "uniE001"}


def load_paths() -> dict[str, str]:
    root = ET.parse(SOURCE_SVG).getroot()
    paths = {
        element.get("id"): element.get("d")
        for element in root.iter()
        if element.tag.endswith("path") and element.get("id") and element.get("d")
    }
    required = {*SEGMENT_IDS, DOT_ID}
    missing = required - paths.keys()
    if missing:
        raise ValueError(f"Missing source paths: {sorted(missing)}")
    return paths


def combined_bounds(path_ids: tuple[str, ...], paths: dict[str, str]) -> tuple[float, float, float, float]:
    pen = BoundsPen(None)
    for path_id in path_ids:
        parse_path(paths[path_id], pen)
    if pen.bounds is None:
        raise ValueError("Expected non-empty path bounds")
    return pen.bounds


def make_glyph(
    path_ids: list[str] | tuple[str, ...],
    paths: dict[str, str],
    transform: tuple[float, float, float, float, float, float],
):
    glyph_pen = TTGlyphPen(None)
    quadratic_pen = Cu2QuPen(glyph_pen, max_err=1.0, reverse_direction=True)
    transformed_pen = TransformPen(quadratic_pen, transform)
    for path_id in path_ids:
        parse_path(paths[path_id], transformed_pen)
    return glyph_pen.glyph()


def glyph_name(character: str) -> str:
    codepoint = ord(character)
    return UV2AGL.get(codepoint, f"uni{codepoint:04X}")


def build_font(paths: dict[str, str], mapping: dict[str, list[str]]) -> tuple[int, int, tuple[float, ...], tuple[float, ...]]:
    segment_bounds = combined_bounds(SEGMENT_IDS, paths)
    dot_bounds = combined_bounds((DOT_ID,), paths)
    scale = SEGMENT_HEIGHT / (segment_bounds[3] - segment_bounds[1])
    cell_center = (segment_bounds[0] + segment_bounds[2]) / 2
    dot_center = (dot_bounds[0] + dot_bounds[2]) / 2
    source_advance = 2 * (dot_center - cell_center)
    advance = round(source_advance * scale)
    cell_left = dot_center - source_advance

    vertical_offset = segment_bounds[3] * scale + (UPM - SEGMENT_HEIGHT) / 2
    cell_transform = (scale, 0, 0, -scale, -cell_left * scale, vertical_offset)
    dot_transform = (scale, 0, 0, -scale, -dot_center * scale, vertical_offset)

    cmap = {0x20: "space", 0xE000: "uniE000", 0xE001: "uniE001"}
    glyph_order = [".notdef", "space"]
    glyphs = {
        ".notdef": make_glyph([], paths, cell_transform),
        "space": make_glyph([], paths, cell_transform),
    }
    metrics = {
        ".notdef": (advance, 0),
        "space": (advance, 0),
    }

    for character, path_ids in mapping.items():
        name = glyph_name(character)
        if character in ZERO_ADVANCE_PUNCTUATION:
            glyphs[name] = make_glyph(path_ids, paths, dot_transform)
            metrics[name] = (0, 0)
        else:
            glyphs[name] = make_glyph(path_ids, paths, cell_transform)
            metrics[name] = (advance, 0)
        glyph_order.append(name)
        cmap[ord(character)] = name

    unsupported_ascii = [
        character for character in map(chr, range(0x21, 0x7F))
        if character not in mapping
    ]
    if unsupported_ascii:
        glyphs["placeholder"] = make_glyph(SEGMENT_IDS, paths, cell_transform)
        metrics["placeholder"] = (advance, 0)
        glyph_order.append("placeholder")
        for character in unsupported_ascii:
            cmap[ord(character)] = "placeholder"

    glyphs["uniE000"] = make_glyph(SEGMENT_IDS, paths, cell_transform)
    glyphs["uniE001"] = make_glyph((*SEGMENT_IDS, DOT_ID), paths, cell_transform)
    metrics["uniE000"] = (advance, 0)
    metrics["uniE001"] = (advance, 0)
    glyph_order.extend(("uniE000", "uniE001"))
    cmap.update(SCAFFOLD_ALIASES)

    builder = FontBuilder(UPM, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    glyf_table = builder.font["glyf"]
    for name, (glyph_advance, _) in metrics.items():
        glyph = glyf_table[name]
        glyph.recalcBounds(glyf_table)
        metrics[name] = (glyph_advance, getattr(glyph, "xMin", 0))
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=UPM, descent=0, lineGap=0)
    builder.setupNameTable(
        {
            "familyName": "TenSegTeen",
            "styleName": "Regular",
            "uniqueFontIdentifier": "TenSegTeen Regular 0.1",
            "fullName": "TenSegTeen Regular",
            "psName": "TenSegTeen-Regular",
            "version": "Version 0.1",
            "copyright": "Copyright 2026 The TenSegTeen Project Authors",
            "description": (
                "Unofficial ten-segment display typeface derived from an illuminated "
                "EP-133 K.O. II LCD. Not affiliated with or endorsed by Teenage Engineering."
            ),
            "licenseDescription": "Licensed under the SIL Open Font License, Version 1.1.",
            "licenseInfoURL": "https://openfontlicense.org/open-font-license-official-text/",
        }
    )
    builder.setupOS2(
        sTypoAscender=UPM,
        sTypoDescender=0,
        sTypoLineGap=0,
        usWinAscent=UPM,
        usWinDescent=0,
        sxHeight=800,
        sCapHeight=SEGMENT_HEIGHT,
    )
    builder.setupPost(isFixedPitch=0, keepGlyphNames=True)
    builder.setupMaxp()

    font = builder.font
    font.recalcTimestamp = False
    font["head"].fontRevision = 0.1
    font["head"].created = 2_082_844_800
    font["head"].modified = 2_082_844_800
    font.save(TTF_PATH)

    font.flavor = "woff2"
    font.save(WOFF2_PATH)

    return advance, round((dot_center - cell_center) * scale), segment_bounds, dot_bounds


def validate_font(mapping: dict[str, list[str]], advance: int) -> None:
    font = TTFont(TTF_PATH)
    cmap = font.getBestCmap()
    expected_codepoints = set(range(0x20, 0x7F)) | {0xE000, 0xE001} | SCAFFOLD_ALIASES.keys()
    if expected_codepoints - cmap.keys():
        raise ValueError(f"Missing cmap entries: {sorted(expected_codepoints - cmap.keys())}")
    for character in ZERO_ADVANCE_PUNCTUATION:
        if font["hmtx"][cmap[ord(character)]][0] != 0:
            raise ValueError(f"{character!r} must have zero advance")
    if font["hmtx"][cmap[ord(" ")]][0] != advance:
        raise ValueError("Space must occupy one full cell")
    for codepoint in (ord("A"), ord("a"), ord("0"), ord("*"), 0xE000, 0xE001):
        if font["hmtx"][cmap[codepoint]][0] != advance:
            raise ValueError(f"Unexpected advance for U+{codepoint:04X}")
    if not WOFF2_PATH.is_file() or WOFF2_PATH.stat().st_size == 0:
        raise ValueError("WOFF2 output is missing")


def main() -> None:
    paths = load_paths()
    mapping = json.loads(MAPPING_JSON.read_text())
    advance, dot_offset, segment_bounds, dot_bounds = build_font(paths, mapping)
    validate_font(mapping, advance)
    print(
        json.dumps(
            {
                "glyphs": len(mapping),
                "advance": advance,
                "dot_offset_from_cell_center": dot_offset,
                "segment_bounds": [round(value, 2) for value in segment_bounds],
                "dot_bounds": [round(value, 2) for value in dot_bounds],
                "ttf_bytes": TTF_PATH.stat().st_size,
                "woff2_bytes": WOFF2_PATH.stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
