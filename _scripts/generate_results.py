#!/usr/bin/env python3
"""
MNHSFL Fencing Results Generator

This script processes tournament results from CSV files and generates
Jekyll blog posts for the MNHSFL website.

Usage:
    python _scripts/generate_results.py

The script will:
1. Scan _fencing-results/ for CSV files
2. For each CSV, create a corresponding blog post in _posts/results/
3. Optionally include intro content from matching .md files
4. Generate a results index page at results/index.md

Note: The _posts/results/ subdirectory is gitignored since these posts
are generated from source files in _fencing-results/. This keeps generated
files out of version control while still making them available to Jekyll.
"""

import csv
from pathlib import Path
from datetime import datetime

class ResultsGenerator:
    """Handles conversion of CSV tournament results to Jekyll blog posts."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.source_dir = self.project_root / "_fencing-results"
        self.posts_dir = self.project_root / "_posts" / "results"
        
    def ensure_output_dirs(self):
        """Create output directories if they don't exist."""
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory ready:")
        print(f"  - Posts: {self.posts_dir}")
        
    def find_csv_files(self):
        """Find all CSV files in the source directory."""
        if not self.source_dir.exists():
            print(f"⚠ Warning: Source directory not found: {self.source_dir}")
            return []
        
        csv_files = list(self.source_dir.glob("*.csv"))
        print(f"✓ Found {len(csv_files)} CSV file(s)")
        return csv_files
    
    def read_intro_content(self, csv_path):
        """Read optional markdown intro content for a tournament.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Tuple of (frontmatter_dict, content_string)
            - frontmatter_dict: parsed YAML frontmatter (empty dict if none)
            - content_string: the markdown content after frontmatter
        """
        md_path = csv_path.with_suffix('.md')
        
        if not md_path.exists():
            print(f"  ℹ No intro content found (looked for {md_path.name})")
            return {}, ""
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for YAML frontmatter
        if content.startswith('---\n'):
            # Split on frontmatter delimiter
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                # Parse frontmatter (simple key: value parsing)
                frontmatter = {}
                frontmatter_lines = parts[1].strip().split('\n')
                for line in frontmatter_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        frontmatter[key] = value
                
                markdown_content = parts[2].strip()
                print(f"  ✓ Found intro content with frontmatter: {md_path.name}")
                return frontmatter, markdown_content
        
        # No frontmatter found, return raw content
        print(f"  ✓ Found intro content: {md_path.name}")
        return {}, content.strip()
    
    def csv_to_markdown_table(self, csv_path):
        """Convert CSV data to a Markdown table.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            String containing the Markdown table
        """
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except csv.Error as e:
            print(f"⚠ CSV format error in {csv_path.name}: {e}")
            return "*CSV format error*\n"
        except UnicodeDecodeError as e:
            print(f"⚠ Encoding error in {csv_path.name}: {e}")
            return "*Encoding error*\n"
        except Exception as e:
            print(f"⚠ Error reading {csv_path.name}: {e}")
            return "*Error reading data*\n"

        if not rows:
            return "*No data available*\n"
        
        # Handle BOM (Byte Order Mark) in header row if present (should be handled by utf8-sig, but double check)
        headers = rows[0]
        if headers and headers[0].startswith('\ufeff'):
            headers[0] = headers[0].lstrip('\ufeff')

        # Ensure all rows have the same number of columns as the header
        inconsistent_rows = [i+1 for i, row in enumerate(rows[1:]) if len(row) != len(headers)]
        if inconsistent_rows:
            print(f"⚠ Warning: Inconsistent row lengths in {csv_path.name} at rows: {inconsistent_rows}")

        # Build markdown table
        table_lines = []
        
        # Header row
        table_lines.append("| " + " | ".join(headers) + " |")
        
        # Separator row
        table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # Data rows
        for row in rows[1:]:
            if len(row) > len(headers):
                print(f"  ⚠ Warning: Row has more columns than header in {csv_path.name}: {row}. Extra data will be truncated.")

            # Pad row if needed to match header length
            padded_row = row + [""] * (len(headers) - len(row))
            table_lines.append("| " + " | ".join(padded_row[:len(headers)]) + " |")
        
        print(f"  ✓ Generated table with {len(rows)-1} data row(s)")
        return "\n".join(table_lines) + "\n"

    # TODO: Find a different way to generate titles for more control
    def generate_title(self, filename):
        """Convert filename to a human-readable title.
        
        Args:
            filename: e.g., 'turkey-tussle-2025'
            
        Returns:
            String like 'Turkey Tussle 2025'
        """
        # Remove extension, replace hyphens with spaces, title case
        return filename.replace('-', ' ').title()
    
    def process_tournament(self, csv_path):
        """Process a single tournament CSV and generate its blog post.
        
        Args:
            csv_path: Path to the tournament CSV file
        """
        filename_stem = csv_path.stem  # e.g., 'turkey-tussle-2025'
        print(f"\nProcessing: {csv_path.name}")

        # Bounce if we exceed file size limit
        max_size_mb = 10
        file_size_mb = csv_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(f"CSV file too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)")
        
        # Read optional intro content and its frontmatter
        intro_frontmatter, intro_content = self.read_intro_content(csv_path)
        
        # Get or generate date
        if 'date' in intro_frontmatter:
            date_value = intro_frontmatter['date']
            # Try parsing as datetime first (YYYY-MM-DD HH:MM:SS or ISO format)
            try:
                # Try full datetime with time
                if ' ' in date_value or 'T' in date_value:
                    # Keep the full datetime string as-is for Jekyll
                    date_str = date_value
                    # Extract just the date part for filename
                    if ' ' in date_value:
                        file_date_str = date_value.split(' ')[0]
                    elif 'T' in date_value:
                        file_date_str = date_value.split('T')[0]
                    else:
                        file_date_str = date_value
                else:
                    # Just a date, validate format
                    datetime.strptime(date_value, '%Y-%m-%d')
                    date_str = date_value
                    file_date_str = date_value
            except ValueError as e:
                raise ValueError(f"Invalid date format in {csv_path.stem}.md. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format. Error: {e}")
        else:
            # No .md file or no date - use today
            date_str = datetime.now().strftime('%Y-%m-%d')
            file_date_str = date_str
            print(f"  ℹ No date found, using today: {date_str}")
        
        # Convert CSV to table
        table_content = self.csv_to_markdown_table(csv_path)
        
        # Generate default title from filename
        default_title = self.generate_title(filename_stem)
        
        # Build Jekyll front matter (merge user frontmatter with defaults)
        frontmatter = {
            'layout': 'post',
            'title': intro_frontmatter.get('title', default_title),
            'date': date_str,
        }
        
        # Add any other frontmatter from intro file (image, excerpt, author, etc.)
        for key, value in intro_frontmatter.items():
            if key not in ['layout', 'title', 'date']:
                frontmatter[key] = value
        
        # Build frontmatter lines
        front_matter_lines = ["---"]
        for key, value in frontmatter.items():
            # Quote strings that might have special chars
            if ' ' in str(value) or ':' in str(value):
                front_matter_lines.append(f"{key}: \"{value}\"")
            else:
                front_matter_lines.append(f"{key}: {value}")
        front_matter_lines.append("---")
        front_matter_lines.append("")
        
        # Combine all parts
        full_content = "\n".join(front_matter_lines)
        
        if intro_content:
            full_content += intro_content + "\n\n"
        
        full_content += table_content
        
        # Jekyll _posts naming convention: YYYY-MM-DD-slug.md (always just date, not time)
        output_filename = f"{file_date_str}-{filename_stem}.md"
        output_path = self.posts_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"  ✓ Generated: {output_path.name}")
    
    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("MNHSFL Fencing Results Generator")
        print("=" * 60)
        
        # Setup
    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("MNHSFL Fencing Results Generator")
        print("=" * 60)
        
        # Setup
        self.ensure_output_dirs()
        
        # Find and process all CSV files
        csv_files = self.find_csv_files()
        
        if not csv_files:
            print("\n⚠ No CSV files found. Nothing to generate.")
            return
        
        # Process each tournament
        for csv_path in csv_files:
            try:
                self.process_tournament(csv_path)
            except Exception as e:
                print(f"  ✗ Error processing {csv_path.name}: {e}")
                raise  # Fail the build on error
        
        print("\n" + "=" * 60)
        print(f"✓ Successfully generated {len(csv_files)} result post(s)")
        print("  Posts: _posts/results/ (gitignored)")
        print("  Results appear on homepage and /news/ feed")
        print("=" * 60)


if __name__ == "__main__":
    generator = ResultsGenerator()
    generator.run()
