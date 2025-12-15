#!/usr/bin/env python3
"""
MNHSFL Fencing Results Converter

This script processes tournament results from CSV files and converts them
to Jekyll blog posts for the MNHSFL website.

Usage:
    python _scripts/convert_fencing_results.py

The script will:
1. Scan _fencing-results/ for CSV files
2. For each CSV, create a corresponding blog post in _posts/results/
3. Optionally include intro content from matching .md files

Note: The _posts/results/ subdirectory is gitignored since these posts
are generated from source files in _fencing-results/. This keeps generated
files out of version control while still making them available to Jekyll.
"""

import csv
from pathlib import Path
from datetime import datetime


class Logger:
    """Handles all console output for the generator."""
    
    def header(self, text: str):
        print("=" * 60)
        print(text)
        print("=" * 60)
    
    def success(self, message: str):
        print(f"✓ {message}")
    
    def info(self, message: str):
        print(f"  ℹ {message}")
    
    def warning(self, message: str):
        print(f"⚠ {message}")
    
    def error(self, message: str):
        print(f"✗ {message}")
    
    def processing(self, filename: str):
        print(f"\nProcessing: {filename}")


class FrontmatterParser:
    """Parses YAML frontmatter from markdown files."""
    
    def parse(self, content: str) -> tuple[dict[str, str], str]:
        if not content.startswith('---\n'):
            return {}, content.strip()
        return self._parse_with_frontmatter(content)
    
    def _parse_with_frontmatter(self, content: str) -> tuple[dict[str, str], str]:
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return {}, content.strip()
        frontmatter = self._parse_frontmatter_lines(parts[1])
        markdown_content = parts[2].strip()
        return frontmatter, markdown_content
    
    def _parse_frontmatter_lines(self, frontmatter_text: str) -> dict[str, str]:
        frontmatter = {}
        for line in frontmatter_text.strip().split('\n'):
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")
        return frontmatter


class FrontmatterBuilder:
    """Builds Jekyll frontmatter from data."""
    
    def build(self, user_data: dict[str, str], defaults: dict[str, str]) -> str:
        merged = self._merge_frontmatter(user_data, defaults)
        return self._format_frontmatter(merged)
    
    def _merge_frontmatter(self, user_data: dict[str, str], defaults: dict[str, str]) -> dict[str, str]:
        result = defaults.copy()
        self._merge_custom_fields(user_data, result)
        self._merge_overridable_fields(user_data, result)
        return result
    
    def _merge_custom_fields(self, user_data: dict[str, str], result: dict[str, str]):
        for key, value in user_data.items():
            if key not in ['layout', 'title', 'date']:
                result[key] = value
    
    def _merge_overridable_fields(self, user_data: dict[str, str], result: dict[str, str]):
        for key in ['title', 'date']:
            if key in user_data:
                result[key] = user_data[key]
    
    def _format_frontmatter(self, data: dict[str, str]) -> str:
        lines = ["---"]
        for key, value in data.items():
            lines.append(self._format_frontmatter_line(key, value))
        lines.extend(["---", ""])
        return "\n".join(lines)
    
    def _format_frontmatter_line(self, key: str, value: str) -> str:
        if ' ' in str(value) or ':' in str(value):
            return f"{key}: \"{value}\""
        return f"{key}: {value}"


class DateExtractor:
    """Extracts and validates dates from frontmatter."""
    
    def extract(self, frontmatter: dict[str, str]) -> tuple[str, str]:
        if 'date' not in frontmatter:
            return self._use_today()
        return self._parse_date(frontmatter['date'])
    
    def _use_today(self) -> tuple[str, str]:
        today = datetime.now().strftime('%Y-%m-%d')
        return today, today
    
    def _parse_date(self, date_value: str) -> tuple[str, str]:
        if ' ' in date_value or 'T' in date_value:
            return self._parse_datetime(date_value)
        self._validate_date_format(date_value)
        return date_value, date_value
    
    def _parse_datetime(self, date_value: str) -> tuple[str, str]:
        separator = ' ' if ' ' in date_value else 'T'
        file_date = date_value.split(separator)[0]
        return date_value, file_date
    
    def _validate_date_format(self, date_str: str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS. Error: {e}")


class CsvReader:
    """Reads and validates CSV files."""
    
    MAX_SIZE_MB = 10
    
    def read(self, csv_path: Path) -> list[list[str]]:
        self._validate_file_size(csv_path)
        return self._read_csv_rows(csv_path)
    
    def _validate_file_size(self, csv_path: Path):
        if (file_size_mb := csv_path.stat().st_size / (1024 * 1024)) > self.MAX_SIZE_MB:
            raise ValueError(f"CSV file too large: {file_size_mb:.1f}MB (max: {self.MAX_SIZE_MB}MB)")
    
    def _read_csv_rows(self, csv_path: Path) -> list[list[str]]:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                return list(csv.reader(f))
        except (csv.Error, UnicodeDecodeError) as e:
            raise ValueError(f"Error reading CSV: {e}")


class TableValidator:
    """Validates CSV table structure."""
    
    def validate(self, rows: list[list[str]], headers: list[str]) -> list[int]:
        if not rows:
            return []
        return [i + 1 for i, row in enumerate(rows) if len(row) != len(headers)]


class TableFormatter:
    """Formats CSV data as Markdown tables."""
    
    def format(self, rows: list[list[str]]) -> str:
        if not rows:
            return "*No data available*\n"
        headers = self._clean_headers(rows[0])
        data_rows = rows[1:]
        return self._build_table(headers, data_rows)
    
    def _clean_headers(self, headers: list[str]) -> list[str]:
        if not (headers and headers[0].startswith('\ufeff')):
            return headers
        cleaned = headers.copy()
        cleaned[0] = cleaned[0].lstrip('\ufeff')
        return cleaned
    
    def _build_table(self, headers: list[str], data_rows: list[list[str]]) -> str:
        lines = []
        lines.append(self._format_header_row(headers))
        lines.append(self._format_separator_row(headers))
        lines.extend(self._format_data_rows(headers, data_rows))
        return "\n".join(lines) + "\n"
    
    def _format_header_row(self, headers: list[str]) -> str:
        return "| " + " | ".join(headers) + " |"
    
    def _format_separator_row(self, headers: list[str]) -> str:
        return "| " + " | ".join(["---"] * len(headers)) + " |"
    
    def _format_data_rows(self, headers: list[str], data_rows: list[list[str]]) -> list[str]:
        formatted = []
        for row in data_rows:
            padded = self._pad_row(row, len(headers))
            formatted.append("| " + " | ".join(padded) + " |")
        return formatted
    
    def _pad_row(self, row: list[str], target_length: int) -> list[str]:
        return (row + [""] * target_length)[:target_length]


class IntroContentReader:
    """Reads intro content from markdown files."""
    
    def read(self, csv_path: Path) -> tuple[dict[str, str], str]:
        if not (md_path := csv_path.with_suffix('.md')).exists():
            return {}, ""
        return self._read_md_file(md_path)
    
    def _read_md_file(self, md_path: Path) -> tuple[dict[str, str], str]:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        parser = FrontmatterParser()
        return parser.parse(content)


class TitleGenerator:
    """Generates titles from filenames."""
    
    def generate(self, filename: str) -> str:
        return filename.replace('-', ' ').title()


class PostWriter:
    """Writes blog posts to disk."""
    
    def write(self, path: Path, content: str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


class PostContentBuilder:
    """Builds complete post content from parts."""
    
    def build(self, frontmatter: str, intro: str, table: str) -> str:
        if not intro:
            return frontmatter + table
        return frontmatter + intro + "\n\n" + table


class OutputFilenameGenerator:
    """Generates output filenames for posts."""
    
    def generate(self, file_date: str, stem: str) -> str:
        return f"{file_date}-{stem}.md"


class ResultsGenerator:
    """Handles conversion of CSV tournament results to Jekyll blog posts."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.source_dir = self.project_root / "_fencing-results"
        self.posts_dir = self.project_root / "_posts" / "results"
        self.logger = Logger()
        self.csv_reader = CsvReader()
        self.table_formatter = TableFormatter()
        self.table_validator = TableValidator()
        self.frontmatter_builder = FrontmatterBuilder()
        self.date_extractor = DateExtractor()
        self.intro_reader = IntroContentReader()
        self.title_generator = TitleGenerator()
        self.post_writer = PostWriter()
        self.content_builder = PostContentBuilder()
        self.filename_generator = OutputFilenameGenerator()
    
    def run(self):
        self.logger.header("MNHSFL Fencing Results Generator")
        self._ensure_output_dirs()
        csv_files = self._find_csv_files()
        self._process_csv_files(csv_files)
    
    def _process_csv_files(self, csv_files: list[Path]):
        if not csv_files:
            self.logger.warning("No CSV files found. Nothing to generate.")
            return
        self._process_all_tournaments(csv_files)
        self._print_summary(len(csv_files))
    
    def _ensure_output_dirs(self):
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.logger.success(f"Output directory ready: {self.posts_dir}")
    
    def _find_csv_files(self) -> list[Path]:
        if not self.source_dir.exists():
            return []
        csv_files = list(self.source_dir.glob("*.csv"))
        self.logger.success(f"Found {len(csv_files)} CSV file(s)")
        return csv_files
    
    def _process_all_tournaments(self, csv_files: list[Path]):
        for csv_path in csv_files:
            try:
                self._process_tournament(csv_path)
            except Exception as e:
                self.logger.error(f"Error processing {csv_path.name}: {e}")
                raise
    
    def _process_tournament(self, csv_path: Path):
        self.logger.processing(csv_path.name)
        rows = self.csv_reader.read(csv_path)
        intro_fm, intro_content = self.intro_reader.read(csv_path)
        date_str, file_date = self.date_extractor.extract(intro_fm)
        self._log_intro_status(intro_fm, intro_content, csv_path)
        self._log_date_info(intro_fm, date_str)
        post_content = self._build_post_content(csv_path, rows, intro_fm, intro_content, date_str)
        output_path = self._write_post(csv_path, post_content, file_date)
        self.logger.success(f"Generated: {output_path.name}")
    
    def _log_intro_status(self, intro_fm: dict, intro_content: str, csv_path: Path):
        if not intro_content and not intro_fm:
            self.logger.info(f"No intro content found (looked for {csv_path.stem}.md)")
            return
        if intro_fm:
            self.logger.success(f"Found intro content with frontmatter: {csv_path.stem}.md")
            return
        self.logger.success(f"Found intro content: {csv_path.stem}.md")
    
    def _build_post_content(self, csv_path: Path, rows: list[list[str]], 
                           intro_fm: dict[str, str], intro_content: str, date_str: str) -> str:
        table = self._generate_table(rows, csv_path)
        frontmatter = self._build_frontmatter(csv_path, intro_fm, date_str)
        return self.content_builder.build(frontmatter, intro_content, table)
    
    def _log_date_info(self, intro_fm: dict, date_str: str):
        if 'date' not in intro_fm:
            self.logger.info(f"No date found, using today: {date_str}")
    
    def _generate_table(self, rows: list[list[str]], csv_path: Path) -> str:
        if not rows:
            return "*No data available*\n"
        headers = rows[0]
        data_rows = rows[1:]
        self._validate_table_structure(data_rows, headers, csv_path)
        table = self.table_formatter.format(rows)
        self.logger.success(f"Generated table with {len(data_rows)} data row(s)")
        return table
    
    def _validate_table_structure(self, data_rows: list[list[str]], 
                                  headers: list[str], csv_path: Path):
        if inconsistent := self.table_validator.validate(data_rows, headers):
            self.logger.warning(f"Inconsistent row lengths in {csv_path.name} at rows: {inconsistent}")
    
    def _build_frontmatter(self, csv_path: Path, intro_fm: dict[str, str], 
                          date_str: str) -> str:
        default_title = self.title_generator.generate(csv_path.stem)
        defaults = {
            'layout': 'post',
            'title': intro_fm.get('title', default_title),
            'date': date_str,
        }
        return self.frontmatter_builder.build(intro_fm, defaults)
    
    def _write_post(self, csv_path: Path, content: str, file_date: str) -> Path:
        filename = self.filename_generator.generate(file_date, csv_path.stem)
        output_path = self.posts_dir / filename
        self.post_writer.write(output_path, content)
        return output_path
    
    def _print_summary(self, count: int):
        self.logger.header(f"✓ Successfully generated {count} result post(s)")
        self.logger.info("Posts: _posts/results/ (gitignored)")
        self.logger.info("Results appear on homepage and /news/ feed")


if __name__ == "__main__":
    generator = ResultsGenerator()
    generator.run()
