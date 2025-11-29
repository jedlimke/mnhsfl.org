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
import os
from pathlib import Path
from datetime import datetime


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
            String content of the .md file, or empty string if not found
        """
        md_path = csv_path.with_suffix('.md')
        
        if md_path.exists():
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"  ✓ Found intro content: {md_path.name}")
                return content
        else:
            print(f"  ℹ No intro content found (looked for {md_path.name})")
            return ""
    
    def csv_to_markdown_table(self, csv_path):
        """Convert CSV data to a Markdown table.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            String containing the Markdown table
        """
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if not rows:
            return "*No data available*\n"
        
        # Build markdown table
        table_lines = []
        
        # Header row
        headers = rows[0]
        table_lines.append("| " + " | ".join(headers) + " |")
        
        # Separator row
        table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # Data rows
        for row in rows[1:]:
            # Pad row if needed to match header length
            padded_row = row + [""] * (len(headers) - len(row))
            table_lines.append("| " + " | ".join(padded_row[:len(headers)]) + " |")
        
        print(f"  ✓ Generated table with {len(rows)-1} data row(s)")
        return "\n".join(table_lines) + "\n"
    
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
        
        # Read optional intro content
        intro_content = self.read_intro_content(csv_path)
        
        # Convert CSV to table
        table_content = self.csv_to_markdown_table(csv_path)
        
        # Generate title
        title = self.generate_title(filename_stem)
        
        # Build Jekyll front matter
        front_matter = [
            "---",
            "layout: default",
            f"title: \"{title}\"",
            "---",
            ""
        ]
        
        # Combine all parts
        full_content = "\n".join(front_matter)
        
        if intro_content:
            full_content += intro_content + "\n\n"
        
        full_content += "## Results\n\n"
        full_content += table_content
        
        # Write output file
        output_path = self.output_dir / f"{filename_stem}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"  ✓ Generated: {output_path.name}")
        
        # Track for index generation
        self.tournaments.append({
            'filename': filename_stem,
            'title': title,
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
            "layout: default",
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
