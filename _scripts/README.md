# Fencing Results Converter

Converts tournament results into Jekyll blog posts automatically.

## How It Works

Each tournament lives in its own subfolder inside `_fencing-results/`. The converter
stitches together all `.csv` and `.md` files in the folder (alphabetically) into a
single post. CSVs become markdown tables; MD files become body text.

**Input:** A result folder containing `_frontmatter.md` plus optional CSV/MD files  
**Output:** A blog post in `_posts/results/` — appears on homepage, `/news/`, and `/results/`

## Quick Start

### For Admins: Adding Results

1. **Create a folder**: `_fencing-results/tournament-name-2026/`
2. **Add `_frontmatter.md`** (required) with at minimum `title` and `date`:
   ```yaml
   ---
   title: "Spring Championship 2026"
   date: 2026-03-15
   excerpt: "Championship results"
   ---
   Optional intro paragraph here.
   ```
3. **Add content files** (optional):
   - `.csv` files → rendered as result tables
   - `.md` files → included as body text
   - Other files (images, etc.) → ignored
4. **Commit and push** — GitHub Actions does the rest

**That's it!** Files are stitched alphabetically, so prefix filenames to control order:
`01-intro.md`, `02-results.csv`.

> ⚠️ **Every folder must have `_frontmatter.md` with `title` and `date` — missing or
> malformed frontmatter blocks deployment.**

### For Developers: Testing Locally

**First, start the development site:**
```bash
docker-compose up
```

**Then, whenever you add/update result folders, regenerate posts:**

```bash
# Option 1: Docker (recommended)
docker build -f _tests/Dockerfile.generate -t mnhsfl-generate . && docker run --rm -v "${PWD}/_posts:/app/_posts" mnhsfl-generate

# Option 2: Python directly
python _scripts/convert_fencing_results.py
```

The site auto-refreshes — just re-run the conversion script to see your changes!

## File Structure

### Source Files (Commit these to Git)

```
_fencing-results/
  README.md                        # Documentation (this pattern)
  tournament-name-2026/
    _frontmatter.md                # Required: title + date (+ optional body)
    01-intro.md                    # Optional: body text (alphabetical order)
    02-results.csv                 # Optional: rendered as table
    photo.jpg                      # Optional: ignored by converter
```

### Generated Files (Cannot be committed — they're .gitignored)

```
_posts/results/
  YYYY-MM-DD-tournament-name-2026.md    # Auto-generated blog posts
```

## _frontmatter.md Reference

```yaml
---
title: "Spring Championship 2026"       # Required
date: 2026-03-15                        # Required (YYYY-MM-DD or with time)
excerpt: "Championship results"         # Optional – used in post previews
author: "Tournament Director"           # Optional – any extra fields pass through
---
Optional intro paragraph that will appear at the top of the post body,
before any other content files.
```

**Required fields:** `title`, `date` — missing either blocks deployment.

## CSV Format

**Any valid CSV works!** First row = headers, rest = data.

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

## Development

### Testing

```bash
# Run all tests (Docker)
docker build -f _tests/Dockerfile.test -t mnhsfl-test . && \
docker run --rm mnhsfl-test

# Run tests (Python)
pytest _tests/test_convert_fencing_results.py -v
```

### The Script

**Location:** `_scripts/convert_fencing_results.py`

**What it does:**
1. Scans `_fencing-results/` for subdirectories
2. For each folder:
   - Validates `_frontmatter.md` (must have `title` and `date`)
   - Reads body from `_frontmatter.md` (if any)
   - Collects `.csv` and `.md` files alphabetically
   - Converts CSVs to tables, includes MD files as body text
   - Writes blog post to `_posts/results/{date}-{folder-name}.md`
   - Fails hard if any folder has invalid/missing `_frontmatter.md`

**Classes:** 11 small, focused classes following single-responsibility principles.

## Deployment

### GitHub Actions Workflow

Push to `master` triggers:
1. **Test Job**: Runs pytest on all tests
2. **Build Job**: Runs converter, builds Jekyll site
3. **Deploy Job**: Publishes to GitHub Pages

See `.github/workflows/cicd.yml`

**Pipeline guarantees:**
- Tests must pass before build
- Build must pass before deploy
- Broken code never reaches production

## Troubleshooting

**Issue:** Posts not showing up
- Ensure results live in a **subfolder**, not at root of `_fencing-results/`
- Verify `_frontmatter.md` exists in the folder
- Check `_frontmatter.md` has both `title` and `date`
- Verify Jekyll is running (`docker-compose up`)

**Issue:** Deployment blocked with validation error
- Read the error message — it tells you exactly which folder and field is wrong
- Fix `_frontmatter.md` and push again

**Issue:** Table looks wrong
- Ensure CSV has consistent column counts
- First row must be headers
- Check for special characters (quote them if needed)