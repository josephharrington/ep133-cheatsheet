# TenSegTeen

TenSegTeen is an unofficial display typeface based on the ten-segment LCD
cells in the Teenage Engineering EP-133 K.O. II. Its segment shapes were
traced from a photograph of an illuminated device. Its core alphanumeric
mappings were checked against text shown on the hardware.

TenSegTeen is not made by, affiliated with, or endorsed by Teenage
Engineering.

[View the interactive font specimen.](https://ep133.joeyh.org/assets/fonts/tensegteen/specimen)

## Character set

The font includes:

- `A-Z` and `a-z`
- `0-9`
- printable ASCII punctuation and symbols
- `U+E000`, an unlit-scaffold cell with all ten segments present
- `U+E001`, the same scaffold cell with its following inter-cell dot
- `¡` and `™`, convenience aliases for the two scaffold glyphs; type them
  with Option-1 and Option-2 on a US Mac keyboard

The punctuation and symbol designs are stylistic extensions. They have not
been verified on the device, and the device may not be able to display them.
Any unmapped printable ASCII character uses an all-segments placeholder so it
cannot trigger a differently spaced fallback font.

The period and comma have zero advance so they light the dot immediately
following the previous cell. Space occupies one full unlit cell. All other
characters use the same cell advance.

The private-use scaffold glyphs are intended for a faint background layer
behind normal display text. Use `U+E001` for every occupied cell except the
last, then `U+E000` for the final cell. The aliases produce the same glyphs;
the Option-key shortcuts depend on the active keyboard layout.

## Source and build

The `source` directory contains the cleaned segment outlines, character map,
and reproducible build script. Run `source/build.py` with Python 3.11 or newer
and FontTools with WOFF support installed. It writes the TTF and WOFF2 files
into this directory. The build normalizes the tightly cropped segment bounds
to the font em while preserving the traced proportions.

## License

TenSegTeen is licensed under the [SIL Open Font License 1.1](OFL.txt).
