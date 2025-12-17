# Minnesota High School Fencing League (MNHSFL) – Website Repository

[![CI/CD](https://github.com/jedlimke/mnhsfl-website/actions/workflows/cicd.yml/badge.svg)](https://github.com/jedlimke/mnhsfl-website/actions/workflows/cicd.yml)

![MNHSFL Banner](assets/mnhsfl-block.svg)

This is the official website for the Minnesota High School Fencing League. It's a static site built with Jekyll and automatically deployed to GitHub Pages.

## What Happens During Deployment

When you push changes to the `master` branch:

1. **Tests Run** - All fencing results generator tests execute to ensure code quality
2. **Results Generated** - CSV files from `_fencing-results/` are converted into blog posts
3. **Site Built** - Jekyll compiles everything into a static website
4. **Deployed** - The site goes live at GitHub Pages automatically

You can:
- Add tournament results by uploading CSV files (with optional markdown frontmatter)
- Create news posts by adding markdown files to `_posts/`
- Update pages by editing content in the repository

Everything is automated - just commit and push!

## Prerequisites

You'll need these tools installed:

- **Git** - Version control ([Download](https://git-scm.com/downloads))
- **Docker** - For local testing and preview ([Download](https://www.docker.com/products/docker-desktop/))
- **VS Code** - Recommended editor ([Download](https://code.visualstudio.com/))

That's it! No Python, Ruby, or Jekyll installation needed.

## Viewing the Site Locally

To preview the site locally and _keep it automatically regenerating_ using Docker:

1. **Build the Docker image:**
   ```sh
   docker-compose build
   ```

2. **Start the Jekyll server:**
   ```sh
   docker-compose up
   ```

3. **Visit in your browser:**
   ```
   http://localhost:4000
   ```

Press `Ctrl+C` to stop the server.

## Git Workflow & Version Control

![Content Update Workflow](assets/basic-workflow.png)

### Basic Workflow

1. **Pull latest code**: `git pull origin master`
2. **Create a branch**: `git checkout -b my-branch-name`
3. **Make your changes** (add posts, update results, etc.)
4. **Stage changes**: `git add .`
5. **Commit**: `git commit -m "Description of changes"`
6. **Push your branch**: `git push origin my-branch-name`
7. **Create a Pull Request** on GitHub
8. **Wait for tests to pass**, then merge
9. Deployment will then happen **automagically**

### Pull Request Best Practices

- Write clear descriptions of what changed
- Keep commits focused on one thing
- Test locally before creating the PR
- Review the changes before requesting merge

**Why use branches and pull requests?**
- Test major changes without affecting the live site
- Automated tests catch errors before deployment
- Keep `master` stable and production-ready
- Get feedback before deploying

**Learn more**: [GitHub's Pull Request Guide](https://github.blog/developer-skills/github/beginners-guide-to-github-creating-a-pull-request/)

## Creating News Posts

Posts go in the `_posts/` directory and must follow this naming convention:

```
YYYY-MM-DD-post-title.md
```

### Basic Post Template

```markdown
---
layout: post
title: "Your Post Title"
date: 2025-12-14
excerpt: "Brief description that appears in listings"
---

Your post content goes here in Markdown format.
```

### Date/Time Format

You can use just a date or include time:

```yaml
date: 2025-12-14                    # Just date
date: 2025-12-14 14:30:00          # Date and time
date: "2025-12-14 14:30:00 -0600"  # With timezone (quote it!)
```

### Example

Create `_posts/2025-12-14-season-opener.md`:

```markdown
---
layout: post
title: "Season Opener This Saturday"
date: 2025-12-14
excerpt: "Join us for the first tournament of the season"
---

The MNHSFL season kicks off this Saturday at 9:00 AM!

Location: Anderson High School
Registration: 8:30 AM
```

## Adding Fencing Results

Results live in `_fencing-results/` and consist of:
- **CSV file** (required) - The tournament data
- **Markdown file** (optional) - Custom frontmatter and intro text

### Naming Convention

Both files must have the same base name:

```
_fencing-results/
  tournament-name-2025.csv
  tournament-name-2025.md    (optional)
```

### CSV Only (Simplest)

Just add a CSV file with your results:

**`_fencing-results/winter-classic-2025.csv`:**
```csv
Fencer,Wins,Losses,Points
Smith Jane,5,1,850
Doe John,4,2,720
```

The system will auto-generate a post with default frontmatter.

### CSV + Markdown (Custom Frontmatter)

Add a matching `.md` file to customize the post:

**`_fencing-results/winter-classic-2025.md`:**
```markdown
---
title: "Winter Classic 2025"
date: 2025-12-20
excerpt: "Championship results from the Winter Classic"
author: "Tournament Director"
---
```

### CSV + Markdown (With Intro Text)

Include content after the frontmatter to add an introduction:

**`_fencing-results/winter-classic-2025.md`:**
```markdown
---
title: "Winter Classic 2025"
date: "2025-12-20 14:30:00"
excerpt: "Championship results from the Winter Classic"
---

The Winter Classic featured 24 fencers competing in épée.
Congratulations to all participants!
```

The intro appears before the results table in the generated post.

## Git Workflow & Version Control

![Content Update Workflow](assets/basic-workflow.png)

### Basic Workflow

1. **Pull latest code**: `git pull origin master`
2. **Create a branch**: `git checkout -b my-branch-name`
3. **Make your changes** (add posts, update results, etc.)
4. **Stage changes**: `git add .`
5. **Commit**: `git commit -m "Description of changes"`
6. **Push your branch**: `git push origin my-branch-name`
7. **Create a Pull Request** on GitHub
8. **Wait for tests to pass**, then merge
9. Deployment will then happen **automagically**

### Working with Branches

For larger changes, use branches:

```bash
# Create a new branch
git checkout -b my-feature-branch

# Make your changes, then commit
git add .
git commit -m "Description of changes"

# Push your branch
git push origin my-feature-branch
```

Then create a **Pull Request** on GitHub to merge your changes.

### Pull Request Etiquette

- Write clear descriptions of what changed
- Keep commits focused on one thing
- Test locally before creating the PR
- Review the changes before requesting merge

**Learn more**: [GitHub's Pull Request Guide](https://github.blog/developer-skills/github/beginners-guide-to-github-creating-a-pull-request/)

### Why Use Branches?

- Test major changes without affecting the live site
- Get feedback before deploying
- Keep `master` stable and production-ready

## Engineering Notes

### CI/CD Pipeline

![CI/CD Pipeline Sequence Diagram](assets/cicd-sequence.png)

**Pipeline guarantees:**
- Tests must pass before build runs
- Build must succeed before deploy runs  
- Broken code never reaches production

**Triggers:**
- Automatic on push to `master`
- Manual via GitHub Actions tab

**Workflow file:** `.github/workflows/cicd.yml`

### Fencing Results Converter

The script is automatically run during build via Github Actions, though it must be **manually run** during local testing.

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

Ultimately, the script just turns CSVs into markdown-formatted `_posts` which is exactly what we need in order to leverage a ton of stuff we **get for free™** when using Jekyll, Liquid, and GitHub Pages.

See [Convert Fencing Results README](_scripts/README.md) for more info.

#### Generating Results Locally (While Developing)

Convert CSV files to posts locally without Python installed.

**One command (Mac/Linux):**
```sh
docker build -f _tests/Dockerfile.generate -t mnhsfl-generate . && docker run --rm -v "${PWD}/_posts:/app/_posts" mnhsfl-generate
```

**For Windows PowerShell:**
```powershell
docker build -f _tests/Dockerfile.generate -t mnhsfl-generate . ; docker run --rm -v "${PWD}/_posts:/app/_posts" mnhsfl-generate
```

**For Windows Command Prompt:**
```cmd
docker build -f _tests/Dockerfile.generate -t mnhsfl-generate . && docker run --rm -v "%cd%/_posts:/app/_posts" mnhsfl-generate
```

The `-v` flag mounts your local `_posts/` directory so generated files appear on your machine!

#### Testing the Converter

Run the full test suite in an isolated Docker environment.

**One command (Mac/Linux/Windows):**
```sh
docker build -f _tests/Dockerfile.test -t mnhsfl-test . && docker run --rm mnhsfl-test
```

This runs all 12 integration tests to ensure the generator works correctly.

### Responsive Tables Plugin

The site includes a custom Jekyll plugin that makes large data tables mobile-friendly without JavaScript.

**How it works:**
- At build time, the plugin scans all HTML tables in posts and pages
- Extracts column headers from `<thead>` elements
- Adds `data-label` attributes to each `<td>` cell with its corresponding header
- CSS transforms tables into stacked cards on mobile devices (≤800px width)

**Implementation:**
- **Plugin:** `_plugins/responsive_tables.rb` (Ruby/Nokogiri)
- **Filter usage:** Applied in `_layouts/post.html` and `_layouts/page.html`
- **CSS:** Mobile card styles in `_sass/base.scss`

**Why this approach:**
- Zero runtime JavaScript overhead
- Data labels generated at build time
- Works perfectly with Markdown tables from CSV converter
- Degrades gracefully if plugin fails

**Location:** `_plugins/responsive_tables.rb`