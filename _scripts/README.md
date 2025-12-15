# Fencing Results Converter

Converts CSV tournament results into Jekyll blog posts automatically.

## How It Works

**Input:**
- CSV file with results (required)
- MD file with frontmatter (optional)

**Output:**
- Blog post with frontmatter + table
- Appears on homepage, /news/, and /results/

## Quick Start

### For Admins: Adding Results

1. **Add CSV**: `_fencing-results/tournament-name-2025.csv`
2. **Add MD** (optional): `_fencing-results/tournament-name-2025.md` with frontmatter
3. **Commit and push** - GitHub Actions does the rest

**That's it!** The site will build the necessary post when it's deployed automatically.

### For Developers: Testing Locally

**First, start the development site:**
```bash
docker-compose up
```

**Then, whenever you add/update CSV or MD files, regenerate posts:**

```bash
# Option 1: Docker (recommended)
docker build -f _tests/Dockerfile.generate -t mnhsfl-generate . && docker run --rm -v "${PWD}/_posts:/app/_posts" mnhsfl-generate

# Option 2: Python directly
python _scripts/convert_fencing_results.py
```

The site auto-refreshes - just re-run the conversion script to see your changes!

## File Structure

### Source Files (Commit these to Git)

```
_fencing-results/
  tournament-name.csv       # Required: Your data
  tournament-name.md        # Optional: Custom frontmatter & intro
```

### Generated Files (Cannot be committed - they're .gitignored)

```
_posts/results/
  YYYY-MM-DD-tournament-name.md    # Auto-generated blog posts
```

## Frontmatter Options

**With custom frontmatter** (`tournament.md`):
```yaml
---
title: "Spring Championship 2025"
date: 2025-03-15
excerpt: "Championship results"
---
Optional intro text here...
```

**Without frontmatter** (CSV only):
- Title: Generated from filename
- Date: Today's date
- No intro content

## CSV Format

**Any valid CSV works!** First row = headers, rest = data.

Example:
```csv
Fencer,Wins,Losses,Points
Smith Jane,5,1,850
Doe John,4,2,720
```

Becomes:
| Fencer | Wins | Losses | Points |
|--------|------|--------|--------|
| Smith Jane | 5 | 1 | 850 |
| Doe John | 4 | 2 | 720 |

## Subdirectories

CSVs and Markdown files need to be in the base `_fencing-results` directory. Files in subdirectories thereof will NOT be processed. 

## Development

### Testing

```bash
# Run all tests (Docker)
docker build -f _tests/Dockerfile.test -t mnhsfl-test . && \
docker run --rm mnhsfl-test

# Run tests with full error output (see validation messages)
docker build -f _tests/Dockerfile.test -t mnhsfl-test . -q && \
docker run --rm -v "${PWD}/_tests/fixtures:/app/_fencing-results:ro" -v "${PWD}/_scripts:/app/_scripts:ro" mnhsfl-test \
python _scripts/convert_fencing_results.py

# Run tests (Python)
pytest _tests/test_convert_fencing_results.py -v
```

### The Script

**Location:** `_scripts/convert_fencing_results.py`

**What it does:**
1. Scans `_fencing-results/` for CSV files (recursively)
2. For each CSV:
   - Reads data
   - Checks for matching `.md` file
   - Extracts frontmatter (or uses defaults)
   - Generates Markdown table
   - Writes blog post to `_posts/results/` (preserving subdirectory structure)

**Classes:** Following "Five Lines of Code" principles - 11 small, focused classes with ≤5 line methods.

## Deployment

### GitHub Actions Workflow

Push to `master` triggers:
1. **Test Job**: Runs pytest on all 16 tests
2. **Build Job**: Runs converter, builds Jekyll site
3. **Deploy Job**: Publishes to GitHub Pages

See `.github/workflows/cicd.yml`

**Pipeline guarantees:**
- Tests must pass before build
- Build must pass before deploy
- Broken code never reaches production

## Troubleshooting

**Issue:** Posts not showing up
- Check CSV is valid (proper headers, comma-separated)
- Check filename matches: `name.csv` and `name.md`
- Check frontmatter has valid YAML
- Check Jekyll is running (`docker-compose up`)

**Issue:** Date is wrong
- Add `date: YYYY-MM-DD` to `.md` frontmatter
- Without frontmatter, uses today's date

**Issue:** Table looks wrong
- Ensure CSV has consistent column counts
- First row must be headers
- Check for special characters (quote them if needed)