#!/usr/bin/env python3
"""
MNHSFL Fencing Results Generator

This script processes tournament results from CSV files and generates
Jekyll-compatible Markdown pages for the MNHSFL website.

Usage:
    python _scripts/generate_results.py

The script will:
1. Scan _fencing-results/ for CSV files
2. For each CSV, create a corresponding results page in results/
3. Optionally include intro content from matching .md files
4. Generate an index page listing all tournaments
"""

import csv
from pathlib import Path

class ResultsGenerator:
    """Handles conversion of CSV tournament results to Jekyll pages."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.source_dir = self.project_root / "_fencing-results"
        self.output_dir = self.project_root / "results"
        self.tournaments = []
        
    def ensure_output_dir(self):
        """Create results directory if it doesn't exist."""
        self.output_dir.mkdir(exist_ok=True)
        print(f"✓ Output directory ready: {self.output_dir}")
        
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
        """Process a single tournament CSV and generate its results page.
        
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
        
        # Convert CSV to table
        table_content = self.csv_to_markdown_table(csv_path)
        
        # Generate default title from filename
        default_title = self.generate_title(filename_stem)
        
        # Build Jekyll front matter (merge user frontmatter with defaults)
        # User-provided frontmatter takes precedence, except layout is always 'post'
        frontmatter = {
            'layout': 'post',  # ALWAYS post, never overridable
            'title': intro_frontmatter.get('title', default_title),
        }
        
        # Add any other frontmatter from intro file (date, image, excerpt, etc.)
        for key, value in intro_frontmatter.items():
            if key not in ['layout', 'title']:  # Don't override layout or title we already set
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
        
        # Write output file
        output_path = self.output_dir / f"{filename_stem}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"  ✓ Generated: {output_path.name}")
        
        # Track for index generation (use the final title)
        self.tournaments.append({
            'filename': filename_stem,
            'title': frontmatter['title'],
            'output_path': output_path
        })
    
    def generate_index(self):
        """Generate an index page listing all tournaments."""
        if not self.tournaments:
            print("\nℹ No tournaments to index")
            return
        
        print(f"\nGenerating index with {len(self.tournaments)} tournament(s)")
        
        # Sort tournaments by filename (reverse chronological if using YYYY format)
        sorted_tournaments = sorted(
            self.tournaments,
            key=lambda x: x['filename'],
            reverse=True
        )
        
        # Build index content
        front_matter = [
            "---",
            "layout: page",
            "title: \"Tournament Results\"",
            "---",
            "",
            "# Tournament Results",
            "",
            "Browse results from MNHSFL tournaments:",
            ""
        ]
        
        content = "\n".join(front_matter)
        
        # Add list of tournaments
        for tournament in sorted_tournaments:
            content += f"- [{tournament['title']}]({tournament['filename']})\n"
        
        # Write index file
        index_path = self.output_dir / "index.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Generated: {index_path.name}")
    
    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("MNHSFL Fencing Results Generator")
        print("=" * 60)
        
        # Setup
        self.ensure_output_dir()
        
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
        
        # Generate index page
        self.generate_index()
        
        print("\n" + "=" * 60)
        print(f"✓ Successfully generated {len(self.tournaments)} result page(s)")
        print("=" * 60)


if __name__ == "__main__":
    generator = ResultsGenerator()
    generator.run()
