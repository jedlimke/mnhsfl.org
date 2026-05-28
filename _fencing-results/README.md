# Fencing Results Source Files

Each tournament result is stored in its own subfolder. Root-level files are ignored by the generator.

## Adding a New Tournament

1. Create a new folder: `_fencing-results/my-tournament-2026/`
2. Add `_frontmatter.md` (required) with at minimum:
   ```yaml
   ---
   title: My Tournament 2026
   date: 2026-03-15
   excerpt: Brief description for the post preview.
   ---
   ```
3. Add content files (all optional, processed alphabetically):
   - `.csv` files → converted to markdown tables
   - `.md` files → included as body text
   - Images/other files → ignored (but can be referenced in markdown)

## Requirements

- `_frontmatter.md` is **required** in every folder — missing it blocks deployment
- `title` and `date` fields in `_frontmatter.md` are **required**
- Date format must be `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`

## Content Order

1. Body text from `_frontmatter.md` (if any, after the `---` block)
2. Other `.csv` and `.md` files in **alphabetical order**

Name your files to control order, e.g. `01-intro.md`, `02-results.csv`.

## Example Structure

```
_fencing-results/
  README.md                        ← this file
  nyx-mens-foil-2026/
    _frontmatter.md                ← required
    01-intro.md                    ← optional body text (comes first alphabetically)
    02-results.csv                 ← optional table data
    action-photo.jpg               ← ignored, but can be linked from intro.md
```
