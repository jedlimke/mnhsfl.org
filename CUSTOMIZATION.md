# Minima Theme Customization Guide

## ⚠️ Important: Minima Version Differences

**GitHub Pages uses Minima 2.5.1**, not Minima 3.0!

The Minima `master` branch README documents v3.0 features like `custom-variables.scss` 
and `custom-styles.scss` hooks that **do not exist** in v2.5.x.

- **Minima 3.0** (unreleased, on `master`): Has `_sass/minima/custom-variables.scss` and `custom-styles.scss` hooks
- **Minima 2.5.1** (GitHub Pages): No such hooks - must override via `assets/main.scss`

Always check the [v2.5.1 README](https://github.com/jekyll/minima/blob/v2.5.1/README.md) for accurate documentation.

## Structure for Minima 2.5.x (Our Setup)

```
_sass/
└── custom.scss          ← All our custom styles go here

assets/
└── main.scss            ← Imports minima, then imports custom.scss
```

## How It Works

In `assets/main.scss`:
```scss
---
---
@import "minima";   // Load the theme first
@import "custom";   // Then override with our styles
```

This is the **prescribed way** per the [v2.5.1 docs](https://github.com/jekyll/minima/blob/v2.5.1/README.md#customization).

## Current Customizations (`_sass/custom.scss`)

### Typography
- **Font**: Neuton (Google Fonts)
- **Font size**: 20px
- **Background**: #F4F2F0 (light beige)

### Colors
- **Brand color**: darkgoldenrod (used for headings)
- **Backgrounds**: White for header and tables

### Tables
- Full-width breakout from content area
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

All changes go in `_sass/custom.scss`. Since this loads AFTER minima, 
your styles will override the theme defaults.

### Change Colors

```css
// Desktop/Large (>800px) - DEFAULT VALUES
:root {
  // Breakpoint values (for reference in JS or debugging)
  --breakpoint-palm: 600px;
  --breakpoint-laptop: 800px;
  
  // Spacing unit - the core spacing value everything derives from
  --spacing-unit: 30px;
  --spacing-unit-half: 15px;          // $spacing-unit / 2
  --spacing-unit-third: 10px;         // $spacing-unit / 3
  
  // Content/wrapper dimensions
  --content-width: 800px;
  --wrapper-max-width: 740px;         // $content-width - ($spacing-unit * 2) = 800 - 60
  --wrapper-padding: 30px;            // $spacing-unit
  
  // Vertical rhythm (margin-bottom on headings, paragraphs, etc.)
  --vertical-rhythm: 15px;            // $spacing-unit / 2
  
  // Table cell padding
  --table-cell-padding-v: 10px;       // $spacing-unit / 3
  --table-cell-padding-h: 15px;       // $spacing-unit / 2
  
  // Header height
  --header-min-height: 55.95px;       // $spacing-unit * 1.865
  
  // Footer/page content vertical padding
  --section-padding: 30px;            // $spacing-unit
  
  // List indent
  --list-indent: 30px;                // $spacing-unit
  
  // Blockquote padding
  --blockquote-padding: 15px;         // $spacing-unit / 2
  
  // Navigation spacing (on mobile, hamburger menu offset)
  --nav-offset: 15px;                 // $spacing-unit / 2
  
  // PROOF-OF-CONCEPT background color
  background-color: lightblue;
}

// Tablet/Medium (601px - 800px)
@media screen and (max-width: 800px) {
  :root {
    // Wrapper gets tighter padding
    --wrapper-max-width: 770px;       // $content-width - $spacing-unit = 800 - 30
    --wrapper-padding: 15px;          // $spacing-unit / 2
    
    // PROOF-OF-CONCEPT background color
    background-color: lightgreen;
  }
}

// Mobile/Small (≤600px)
@media screen and (max-width: 600px) {
  :root {
    // Same as tablet for most values, but this is where
    // Minima switches to mobile navigation (hamburger menu)
    // and footer columns stack vertically
    
    // You might want tighter spacing on mobile:
    // --spacing-unit: 20px;          // Optional: reduce base spacing
    // --wrapper-padding: 10px;       // Optional: even tighter
    
    // PROOF-OF-CONCEPT background color
    background-color: lightcoral;
  }
}
```