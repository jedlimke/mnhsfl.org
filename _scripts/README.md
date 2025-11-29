# Fencing Results Build System Documentation

## Overview
This system automates the conversion of tournament fencing results from CSV files into properly formatted pages on the MNHSFL website. It's designed to be maintainable by non-developers while leveraging GitHub Actions for automation.

## Architecture

### The Problem
MNHSFL tournament results arrive in CSV format (consistent but potentially ugly formatting). We need to:
1. Accept these CSVs from non-technical admins
2. Transform them into properly themed web pages
3. Keep the process simple and fail-safe
4. Maintain static site benefits (no dynamic processing on the live site)

### The Solution
A three-stage build pipeline:
1. **Source files** → 2. **Python transformation** → 3. **Jekyll theming** → 4. **Static HTML site**

## File Structure

```
_fencing-results/          # Source data (underscore = not published by Jekyll)
  tournament-name.csv      # Raw results data
  tournament-name.md       # (Optional) Editorial intro content
  
_scripts/                  # Build automation
  generate_results.py      # Python script that does the transformation
  script-notes.md          # This file
  
results/                   # Generated output (appears in built site only)
  tournament-name.md       # Generated Jekyll pages
  index.md                 # Generated tournament listing
```

## How It Works

### Step 1: Python Script (`generate_results.py`)
**When:** Runs as a GitHub Actions step BEFORE Jekyll builds  
**What it does:**
1. Scans `_fencing-results/` for all `.csv` files
2. For each CSV file (e.g., `turkey-tussle-2025.csv`):
   - Reads the CSV data
   - Looks for matching `.md` file (e.g., `turkey-tussle-2025.md`)
   - Creates a new Markdown file in `results/` with:
     - Jekyll front matter (layout, title, etc.)
     - Optional intro content from the `.md` file
     - HTML/Markdown table generated from CSV data
3. Generates `results/index.md` listing all tournaments

**Why Python:** 
- Pre-installed in GitHub Actions runners
- Built-in `csv` module for parsing
- Easy to read/maintain
- No compilation needed

### Step 2: Jekyll Build
**When:** Runs immediately after Python script  
**What it does:**
1. Picks up generated `.md` files from `results/`
2. Applies site theme/layout/styling
3. Generates final HTML pages

**Why this separation:**
- Script only handles data transformation
- Jekyll handles all presentation/theming
- Site design changes don't require script updates
- Leverages Jekyll's built-in templating system

### Step 3: GitHub Pages Deploy
Standard Jekyll deployment - serves the static HTML.

## Usage (For MNHSFL Admins)

### Adding Tournament Results
1. Create CSV file: `_fencing-results/tournament-name-YYYY.csv`
2. (Optional) Create intro: `_fencing-results/tournament-name-YYYY.md`
3. Commit and push to GitHub
4. GitHub Actions automatically builds and deploys

### File Naming Convention
- Use kebab-case: `spring-championship-2025.csv`
- Match CSV and MD filenames exactly (except extension)
- The filename becomes the URL slug: `/results/spring-championship-2025/`

### CSV Format
(To be determined based on actual tournament result format)  
For testing: Simple two-column format (header row + data rows)

### Optional MD File
Can include any markdown content that will appear before the results table:
- Tournament description
- Date/location info
- Notes about scoring
- Photos/links

If no `.md` file exists, that's fine - just the table will appear.

## Build Failure Scenarios
The script runs BEFORE deployment, so:
- Malformed CSV = build fails, no broken site deployed
- Missing required data = build fails with error message
- Bad front matter = build fails

This "fail fast" approach prevents publishing broken pages.

## Maintenance Notes

### Modifying the Script
- Script is in `_scripts/generate_results.py`
- Uses only Python stdlib where possible
- Comments explain each section
- Test locally: `python _scripts/generate_results.py`

### Modifying Page Layout
- Edit Jekyll layouts/includes (not the script)
- Front matter in script can reference different layouts

### Future Enhancements
- Support multiple CSV formats
- Generate statistics/summaries
- Add photo galleries
- Create tournament archive by year

## Why This Approach?

### Alternatives We Avoided
1. **Manual HTML editing:** Error-prone, time-consuming
2. **WYSIWYG editor:** Defeats the purpose of version control
3. **Database + dynamic site:** Overkill for static results data
4. **Client-side processing:** SEO issues, requires JavaScript

### Benefits of Our Approach
- ✅ Version controlled source data (CSVs)
- ✅ Automated transformation (no manual HTML)
- ✅ Static output (fast, secure, simple hosting)
- ✅ Technical enough to be powerful
- ✅ Simple enough to maintain
- ✅ Fails safely (bad data won't break the site)

## Dependencies
- Python 3.x (pre-installed in GitHub Actions)
- Standard library only (no pip packages required initially)
- Jekyll (already part of GitHub Pages)

---

**Last Updated:** November 28, 2025  
**Created By:** Workshop build system setup
