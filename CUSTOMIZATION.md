# Minima Theme Customization Guide

## Structure Overview

This site uses the official Minima theme customization approach. Here's how it works:

```
_sass/
├── minima/
│   ├── custom-variables.scss  ← Override theme variables BEFORE Minima loads
│   └── custom-styles.scss     ← Add custom styles AFTER Minima loads
└── custom.scss                ← Old file (ignored, kept for reference)

assets/
└── main.scss                  ← Just imports "minima" (which auto-loads our custom files)
```

## How It Works

When you `@import "minima"` in `assets/main.scss`, Minima automatically:

1. **Loads** `_sass/minima/custom-variables.scss` 
2. **Then** loads the theme's default variables
3. **Then** loads the theme's base styles
4. **Finally** loads `_sass/minima/custom-styles.scss`

This means:
- **Variables** go in `custom-variables.scss`
- **Styles** go in `custom-styles.scss`

## Current Customizations

### Variables (`_sass/minima/custom-variables.scss`)

- **Font**: Neuton (Google Fonts)
- **Font size**: 20px
- **Background**: #F4F2F0
- **Brand color**: darkgoldenrod
- **Content width**: 800px (readable text width)
- **Table breakout padding**: 30px (space on viewport edges)

### Styles (`_sass/minima/custom-styles.scss`)

- **Headings**: Gold color with bottom borders
- **Tables**: Full-width breakout from content area
  - Width: 100vw - 60px (30px padding each side)
  - Centered in viewport
  - White background
  - Responsive padding on mobile

## The Table Breakout Technique

The full-width table effect uses a CSS trick:

```scss
table {
  width: 100vw;                                  // Full viewport width
  margin-left: calc(-1 * (100vw - 100%) / 2);   // Pull left to viewport edge
  margin-right: calc(-1 * (100vw - 100%) / 2);  // Pull right to viewport edge
  padding-left: 30px;                            // Keep content off edge
  padding-right: 30px;                           // Keep content off edge
}
```

This works because:
- Content is centered with `max-width` and `margin: auto`
- The calc finds the distance from content edge to viewport edge
- Negative margins pull the table to viewport edges
- Padding keeps table content readable

## Making Changes

### Change Colors

Edit `_sass/minima/custom-variables.scss`:

```scss
$background-color: #F4F2F0 !default;  // Page background
$brand-color: darkgoldenrod !default; // Headings, links
$text-color: #111 !default;           // Body text
```

### Change Fonts

Edit `_sass/minima/custom-variables.scss`:

```scss
$base-font-family: "Neuton", serif !default;
$base-font-size: 20px !default;
```

Don't forget to import the font in `_sass/minima/custom-styles.scss`:

```scss
@import url('https://fonts.googleapis.com/css2?family=YourFont&display=swap');
```

### Adjust Table Width

Edit the padding in `_sass/minima/custom-variables.scss`:

```scss
$table-breakout-padding: 30px;  // Change to 15px, 50px, etc.
```

### Change Content Width

Edit `_sass/minima/custom-variables.scss`:

```scss
$content-width: 800px !default;  // Change to 900px, 1000px, etc.
```

Note: Tables will still break out to full width!

## Responsive Behavior

Tables automatically adjust on small screens:
- Padding reduces to 15px
- Font size reduces to 0.9em
- Cell padding tightens

Breakpoint is at `$on-palm: 600px`.

## Alternative: Wrapper Class

If the calc trick doesn't work in some browsers, use this HTML wrapper:

```html
<div class="table-full-width">
  <table>
    ...
  </table>
</div>
```

The `.table-full-width` class is already defined in `custom-styles.scss`.

## Testing Changes

1. Edit the SCSS files
2. Jekyll will auto-rebuild (watch for "Regenerating..." in terminal)
3. Browser will auto-reload (LiveReload is enabled)
4. Check http://localhost:4000

## Available Minima Skins

Change the skin in `_config.yml`:

```yaml
minima:
  skin: solarized  # Options: auto, classic, dark, solarized, solarized-dark
```

Each skin has different color schemes. Custom variables override the skin colors.

## Resources

- [Minima GitHub](https://github.com/jekyll/minima)
- [Minima Customization](https://github.com/jekyll/minima#customization)
- [Jekyll SCSS Documentation](https://jekyllrb.com/docs/assets/)
