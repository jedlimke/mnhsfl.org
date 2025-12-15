# Fencing Results Build System Documentation

## Overview
This system automates the conversion of tournament fencing results from CSV files into blog posts on the MNHSFL website.

## Quick Test (Docker - Recommended)

**No Python installation needed!** Run from project root:

```bash
docker build -f _tests/Dockerfile.test -t mnhsfl-test . && docker run --rm mnhsfl-test
```

This ensures the generator works correctly in a clean environment.

## Setup (Local Development)

For local development without Docker:

```bash
pip install pytest
```

## Quick Start (Local)

```bash
# Generate result posts from CSV files
python _scripts/generate_results.py

# Run tests
pytest _tests/test_generate_results.py -v
```
pytest _tests/test_generate_results.py -v
```

Results will be:
- Generated as blog posts in `_posts/results/` (gitignored)
- Listed on dedicated index page at `results/index.md`
- Displayed on homepage and /news/ feed automatically

## Testing

### Run Tests

```bash
# Run all integration tests
pytest _tests/test_generate_results.py -v

# Run specific test class
pytest _tests/test_generate_results.py::TestResultsGeneration -v

# Run specific test
pytest _tests/test_generate_results.py::TestResultsGeneration::test_csv_with_frontmatter_and_intro -v

# Run tests matching a pattern
pytest _tests/test_generate_results.py -k "frontmatter" -v
```

### Test Organization

Tests live in `_tests/` at the project root:
```
_tests/
├── test_generate_results.py    # Integration tests
└── fixtures/                    # CSV and MD files together (mirrors real usage)
    ├── basic-tournament.csv
    ├── spring-open.csv
    ├── spring-open.md           # Paired with CSV
    ├── winter-classic.csv
    ├── winter-classic.md        # Paired with CSV
    └── ...
```

All tests follow the **AAA (Arrange-Act-Assert) pattern** with clear comments.

Tests use **pytest** with:
- Fixtures for automatic setup/teardown
- Parameterized tests for multiple scenarios
- Clean assertion syntax

### Test Coverage

The test suite (`_tests/test_generate_results.py`) covers:
- ✅ CSV only (no .md file) - uses default frontmatter
- ✅ CSV with frontmatter (no intro content)
- ✅ CSV with frontmatter AND intro content
- ✅ Inconsistent column counts (padding/truncation)
- ✅ Empty CSV files
- ✅ UTF-8 BOM handling
- ✅ Multiple CSV files (parameterized: 1, 3, 5 files)
- ✅ Special characters in frontmatter (colons, quotes)
- ✅ Edge cases (no source dir, no CSV files)

Total: 12 test cases (10 base + 2 parameterized variants)

### CI/CD

Tests run automatically on GitHub Actions as part of the deployment workflow:
- **Test job** runs first with pytest validation
- **Build job** only runs if tests pass (generates results + builds Jekyll)
- **Deploy job** only runs if build succeeds

This ensures broken code never gets deployed to production.

Workflow triggers:
- Pushing to `master` branch
- Manual workflow dispatch

See `.github/workflows/cicd.yml` (integrated test + build + deploy)

## Architecture

### The Problem
MNHSFL tournament results arrive in CSV format. We need to:
1. Accept these CSVs from non-technical admins
2. Transform them into properly formatted web pages
3. Keep the process simple and fail-safe
4. Keep development clean (no test data in version control)

### The Solution
A three-stage build pipeline:
1. **Source files** → 2. **Python transformation** → 3. **Jekyll rendering** → 4. **Static HTML site**

## File Structure

```  
_scripts/                  # Build automation
  generate_results.py      # Python script that does the transformation
  README.md                # This file

_fencing-results/          # Source data (committed to git)
  tournament-name.csv      # Raw results data (REQUIRED)
  tournament-name.md       # Metadata and intro content (OPTIONAL)
  
_posts/results/            # Generated blog posts (gitignored, auto-generated)
  YYYY-MM-DD-tournament-name.md  # Posts created by script
  
results/                   # Index page (committed to git)
  index.md                 # Index page listing all results (always generated)
```

## How It Works

### Output Structure
**Generated posts:** `_posts/results/` subdirectory (gitignored)  
**Layout:** `post` (blog post with `categories: results`)  
**Naming:** Jekyll convention (e.g., `2025-11-28-turkey-tussle-2025.md`)  
**Date handling:** Uses date from .md frontmatter if present, otherwise today's date  
**Benefits:** 
- Results appear automatically in blog feed and homepage
- Jekyll picks up subdirectory posts automatically
- Gitignored to keep development clean (generated from source)
- No mode switching needed - same workflow for dev and production

### What the Script Does:
1. Scans `_fencing-results/` for all `.csv` files
2. For each CSV file (e.g., `turkey-tussle-2025.csv`):
   - Reads the CSV data
   - Looks for optional matching `.md` file (e.g., `turkey-tussle-2025.md`)
   - Extracts metadata from frontmatter if present (title, date, image)
   - Uses sensible defaults if no frontmatter found
   - Creates blog post in `_posts/results/` with:
     - Jekyll front matter (layout: post, title, date, categories: results)
     - Optional intro content from the `.md` file
     - Markdown table generated from CSV data
3. Generates `results/index.md` listing all tournaments with links

### Jekyll Build
**When:** Runs after Python script (or continuously during `docker-compose up`)  
**What it does:**
1. Processes all posts from `_posts/` (including `_posts/results/` subdirectory)
2. Results posts appear on homepage grid and /news/ feed alongside announcements
3. `results/index.md` provides a dedicated results landing page
4. Can filter by `categories: results` to separate results from announcements

**Why this separation:**
- Script only handles data transformation
- Jekyll handles all presentation/theming
- Site design changes don't require script updates
- Leverages Jekyll's built-in templating and collections system

### GitHub Pages Deploy
Standard Jekyll deployment - serves the static HTML.

## Usage (For MNHSFL Admins)

### Adding Tournament Results

1. **Create CSV file**: `_fencing-results/tournament-name-YYYY.csv`
   - Include tournament data with header row

2. **Create metadata file** (REQUIRED): `_fencing-results/tournament-name-YYYY.md`
   - Must include frontmatter with required `date` field
   - Example:
     ```markdown
     ---
     title: Spring Championship 2025
     date: 2025-03-15
     excerpt: Results from our spring championship tournament
     image: https://example.com/tournament-photo.jpg  # Optional
     ---
     
     Tournament description and intro content here...
     ```

3. **Run the script locally** (during development):
   ```bash
   python _scripts/generate_results.py
   ```
   
   This will:
   - Generate posts to `_posts/results/` (gitignored)
   - Update `results/index.md` with tournament list
   - Show success summary

4. **Test locally with Jekyll**:
   ```bash
   docker-compose up
   # OR
   bundle exec jekyll serve
   ```
   
   Results will appear:
   - On homepage grid (up to 5 posts)
   - In /news/ feed alongside announcements
   - On dedicated /results/ index page

5. **Commit source files only** and push to GitHub `master`:
   ```bash
   git add _fencing-results/*.csv _fencing-results/*.md results/index.md
   git commit -m "Add tournament results"
   git push
   ```
   
   Note: Don't commit `_posts/results/` - it's gitignored and regenerated automatically

6. **GitHub Actions will**:
   - Run the Python script to regenerate posts
   - Build Jekyll site with all posts
   - Deploy to GitHub Pages

### File Naming Convention
- Use kebab-case: `spring-championship-2025.csv`
- Match CSV and MD filenames exactly (except extension)
- The filename becomes part of the URL: `/YYYY/MM/DD/spring-championship-2025/`

### Optional MD File Frontmatter
Since the `.md` file is optional, all frontmatter fields have sensible defaults:
- `date`: YYYY-MM-DD format (defaults to today if missing)
- `title`: Display title (defaults to prettified filename)
- `excerpt`: Short description (optional - improves homepage cards)
- `image`: Featured image URL (optional - adds hero image)
- `author`: Author name (optional)

### CSV Format
Any CSV format works! The script converts it to a Markdown table as-is:
- First row = table headers
- Remaining rows = data
- Keep files under 10MB

The content-agnostic approach means admins have flexibility in what data to include.

## Version Control Strategy

### What Gets Committed
✅ **Source files:**
- `_fencing-results/*.csv` (required data)
- `_fencing-results/*.md` (optional metadata)
- `results/index.md` (generated index page)
- `_scripts/generate_results.py` (the script itself)

❌ **Generated files (gitignored):**
- `_posts/results/*.md` (regenerated from source)

### Why This Approach
- Source files are the "source of truth"
- Generated posts can always be recreated from CSV + optional MD
- Keeps git history clean (no diffs on generated content)
- Same workflow for development and production
- No risk of forgetting to run script before committing

## Build Process

### Local Development
1. Add/edit CSV files in `_fencing-results/`
2. Optionally create/edit matching `.md` files
3. Run `python _scripts/generate_results.py`
4. Test with Jekyll (`docker-compose up`)
5. Commit source files only

### Production Deployment
1. Push commits to GitHub
2. GitHub Actions runs automatically:
   - Checks out code
   - Runs Python script
   - Builds Jekyll site
   - Deploys to GitHub Pages

The script runs in both environments, ensuring consistency.

## Maintenance Notes

### Testing Locally
```bash
# Generate posts from CSV files
python _scripts/generate_results.py

# Start Jekyll server to see results
docker-compose up
# OR
bundle exec jekyll serve

# Visit http://localhost:4000 to see:
# - Homepage grid with result cards
# - /news/ feed with all posts
# - /results/ dedicated index page
```

### Cleaning Generated Files
Since `_posts/results/` is gitignored, you can:
```bash
# Delete all generated posts
rm -rf _posts/results/

# Regenerate from source
python _scripts/generate_results.py
```

### Modifying the Script
- Script is in `_scripts/generate_results.py`
- Comments explain each section
- Always test locally before committing

### Modifying Results Display
- Edit `_layouts/post.html` for individual result pages
- Edit `_sass/post.scss` for styling
- Edit `_layouts/home.html` for homepage grid
- Results automatically inherit blog post layout

### Future Enhancements
- Support for result photos/galleries
- Tournament statistics/summaries
- Results filtering by weapon/division
- Year-based archives

## Why This Approach?

### Alternatives We Avoided
1. **Manual HTML editing:** Error-prone, time-consuming
2. **WYSIWYG editor:** Defeats the purpose of version control
3. **Database + dynamic site:** Overkill for static results data
4. **Client-side processing:** SEO issues, requires JavaScript
5. **Dev vs production modes:** Unnecessary complexity

### Benefits of Our Approach
- ✅ Version controlled source data (CSVs + optional MDs)
- ✅ Automated transformation (no manual HTML)
- ✅ Static output (fast, secure, simple hosting)
- ✅ Clean git history (only source files committed)
- ✅ Same workflow for dev and production
- ✅ Jekyll subdirectory support (automatic post collection)
- ✅ Optional metadata files (works without .md files)
- ✅ Simple and maintainable (no mode switching)

## Dependencies
- Python 3.x (pre-installed in GitHub Actions)
- Standard library only (no pip packages required)
- Jekyll (already part of GitHub Pages)

---

**Last Updated:** January 2025  
**Created By:** @jedlimke
