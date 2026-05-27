#!/usr/bin/env python3
"""
MNHSFL Fencing Results Converter

This script processes tournament results from folders and converts them
to Jekyll blog posts for the MNHSFL website.

Usage:
    python _scripts/convert_fencing_results.py

Each result folder inside _fencing-results/ becomes one post.

Folder structure:
    _fencing-results/
      my-tournament-2026/
        _frontmatter.md    # Required: must contain 'title' and 'date' fields
        results.csv        # Optional: converted to a markdown table
        intro.md           # Optional: included as body text
        photo.jpg          # Optional: ignored (but can be referenced in markdown)

Files are stitched together in alphabetical order. The body of _frontmatter.md
is always placed first, followed by other .csv and .md files alphabetically.
Non-CSV/MD files are silently ignored.

Root-level files in _fencing-results/ are ignored. Only subdirectories are
processed. A README.md at the root is conventional.

Note: The _posts/results/ subdirectory is gitignored since these posts
are generated from source files in _fencing-results/.
"""

import csv
import re
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class TournamentData:
    """All the data needed to process a result folder."""
    frontmatter: dict[str, str]      # Parsed from _frontmatter.md
    fm_body: str                     # Body content of _frontmatter.md (after ---)
    content_files: list[Path]        # CSV/MD files in folder, alphabetical order
    date_str: str                    # Full date string for Jekyll frontmatter
    file_date: str                   # Date part only for output filename


class Logger:
    """Handles all console output for the generator."""

    def header(self, text: str):
        print("=" * 60)
        print(text)
        print("=" * 60)

    def success(self, message: str):
        print(f"\u2705\t{message}")

    def info(self, message: str):
        print(f"\u2139\ufe0f\t{message}")

    def warning(self, message: str):
        print(f"\u26a0\ufe0f\t{message}")

    def error(self, message: str):
        print(f"\u274c\t{message}")

    def processing(self, name: str):
        print(f"\nProcessing: {name}")


class FrontmatterParser:
    """Parses YAML frontmatter from markdown files."""

    def parse(self, content: str) -> tuple[dict[str, str], str]:
        if not content.startswith('---\n'):
            return {}, content.strip()

        return self._parse_with_frontmatter(content)

    def _parse_with_frontmatter(self, content: str) -> tuple[dict[str, str], str]:
        if len(parts := content.split('---\n', 2)) < 3:
            return {}, content.strip()

        return self._parse_frontmatter_lines(parts[1]), parts[2].strip()

    def _parse_frontmatter_lines(self, frontmatter_text: str) -> dict[str, str]:
        return {
            (parts := line.split(':', 1))[0].strip(): parts[1].strip().strip('"').strip("'")
            for line in frontmatter_text.strip().split('\n')
            if ':' in line
        }


class FolderValidator:
    """Validates that a result folder has a proper _frontmatter.md with required fields."""

    FRONTMATTER_FILE = "_frontmatter.md"

    def validate(self, folder: Path) -> tuple[dict[str, str], str]:
        """Returns (frontmatter_dict, body_content) or raises ValueError."""
        fm_path = folder / self.FRONTMATTER_FILE

        if not fm_path.exists():
            raise ValueError(
                f"Missing required file: _frontmatter.md\n"
                f"\tEvery result folder must contain _frontmatter.md with 'title' and 'date'."
            )

        content = fm_path.read_text(encoding='utf-8')
        parser = FrontmatterParser()
        fm, body = parser.parse(content)

        if 'title' not in fm:
            raise ValueError(
                f"_frontmatter.md is missing required 'title' field\n"
                f"\tAdd 'title: Your Tournament Name' to {folder.name}/_frontmatter.md"
            )

        if 'date' not in fm:
            raise ValueError(
                f"_frontmatter.md is missing required 'date' field\n"
                f"\tAdd 'date: YYYY-MM-DD' to {folder.name}/_frontmatter.md"
            )

        return fm, body


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
            return f'{key}: "{value}"'
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
        self._validate_date_format(file_date)
        return date_value, file_date

    def _validate_date_format(self, date_str: str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError(
                f"Invalid date format: '{date_str}'\n"
                f"\tExpected format: YYYY-MM-DD (e.g., 2025-03-15)\n"
                f"\tOr with time: YYYY-MM-DD HH:MM:SS (e.g., 2025-03-15 14:30:00)"
            )


class CsvReader:
    """Reads and validates CSV files."""

    MAX_SIZE_MB = 10

    def read(self, csv_path: Path) -> list[list[str]]:
        self._validate_file_size(csv_path)
        return self._read_csv_rows(csv_path)

    def _validate_file_size(self, csv_path: Path):
        if (file_size_mb := csv_path.stat().st_size / (1024 * 1024)) > self.MAX_SIZE_MB:
            raise ValueError(
                f"CSV file too large: {file_size_mb:.1f}MB (max: {self.MAX_SIZE_MB}MB)\n"
                f"\tConsider splitting into multiple tournament files."
            )

    def _read_csv_rows(self, csv_path: Path) -> list[list[str]]:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                return list(csv.reader(f))
        except csv.Error as e:
            raise ValueError(
                f"Malformed CSV file\n"
                f"\t{e}\n"
                f"\tCheck for unclosed quotes, missing commas, or extra delimiters."
            )
        except UnicodeDecodeError as e:
            raise ValueError(
                f"File encoding error\n"
                f"\t{e}\n"
                f"\tSave the CSV file as UTF-8 encoding.\n"
                f"\tIs the file actually a CSV?"
            )


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


class PostWriter:
    """Writes blog posts to disk."""

    def write(self, path: Path, content: str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


class OutputFilenameGenerator:
    """Generates output filenames for posts."""

    def generate(self, file_date: str, stem: str) -> str:
        return f"{file_date}-{stem}.md"


class ResultsGenerator:
    """Handles conversion of result folders to Jekyll blog posts."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.source_dir = self.project_root / "_fencing-results"
        self.posts_dir = self.project_root / "_posts" / "results"
        self.assets_dir = self.project_root / "assets" / "results"
        self.logger = Logger()
        self.csv_reader = CsvReader()
        self.table_formatter = TableFormatter()
        self.table_validator = TableValidator()
        self.frontmatter_builder = FrontmatterBuilder()
        self.date_extractor = DateExtractor()
        self.folder_validator = FolderValidator()
        self.post_writer = PostWriter()
        self.filename_generator = OutputFilenameGenerator()

    def run(self):
        self.logger.header("MNHSFL Fencing Results Generator")
        self._ensure_output_dirs()
        folders = self._find_result_folders()
        self._process_folders(folders)

    # -------------------------------------------------------------------------
    # Folder discovery
    # -------------------------------------------------------------------------

    def _find_result_folders(self) -> list[Path]:
        if not self.source_dir.exists():
            return []

        folders = sorted(d for d in self.source_dir.iterdir() if d.is_dir())
        self.logger.success(f"Found {len(folders)} result folder(s)")
        return folders

    # -------------------------------------------------------------------------
    # Processing pipeline
    # -------------------------------------------------------------------------

    def _process_folders(self, folders: list[Path]):
        if not folders:
            self.logger.warning("No result folders found. Nothing to generate.")
            return

        if errors := self._collect_folder_errors(folders):
            self._print_error_summary(errors)
            raise SystemExit(1)

    def _collect_folder_errors(self, folders: list[Path]) -> list[tuple[str, str]]:
        return [error for folder in folders
                if (error := self._try_process_folder(folder))]

    def _try_process_folder(self, folder: Path) -> tuple[str, str] | None:
        try:
            self._process_folder(folder)
            return None
        except (ValueError, Exception) as e:
            self._log_folder_error(folder, e)
            return (folder.name, str(e))

    def _process_folder(self, folder: Path):
        self.logger.processing(folder.name)

        data = self._read_folder_data(folder)
        self._log_date_info(data.frontmatter, data.date_str)
        self._copy_folder_assets(folder)

        output_path = self._build_and_write_post(folder, data)
        self.logger.success(f"Generated: {output_path.name}")

    # -------------------------------------------------------------------------
    # Data reading
    # -------------------------------------------------------------------------

    def _read_folder_data(self, folder: Path) -> TournamentData:
        fm, fm_body = self.folder_validator.validate(folder)
        date_str, file_date = self.date_extractor.extract(fm)
        content_files = self._collect_content_files(folder)
        return TournamentData(fm, fm_body, content_files, date_str, file_date)

    def _collect_content_files(self, folder: Path) -> list[Path]:
        return sorted(
            (f for f in folder.iterdir()
             if f.is_file()
             and f.name != '_frontmatter.md'
             and f.suffix in ('.csv', '.md')),
            key=lambda f: f.name,
        )

    # -------------------------------------------------------------------------
    # Post building
    # -------------------------------------------------------------------------

    def _build_and_write_post(self, folder: Path, data: TournamentData) -> Path:
        frontmatter_str = self._build_frontmatter(folder, data.frontmatter, data.date_str)
        body = self._build_body(data, folder.name)
        content = frontmatter_str + body
        return self._write_post(folder, content, data.file_date)

    def _build_frontmatter(self, folder: Path, fm_data: dict[str, str], date_str: str) -> str:
        fm_copy = dict(fm_data)
        if 'excerpt' not in fm_copy:
            fm_copy['excerpt'] = ' '

        defaults = {
            'layout': 'post',
            'title': fm_copy.get('title', folder.name),
            'date': date_str,
            'categories': 'results',
        }
        return self.frontmatter_builder.build(fm_copy, defaults)

    def _build_body(self, data: TournamentData, folder_name: str) -> str:
        parts = []

        if data.fm_body:
            parts.append(data.fm_body.strip())

        for content_file in data.content_files:
            if content_file.suffix == '.csv':
                part = self._csv_to_table(content_file)
            else:
                part = content_file.read_text(encoding='utf-8').strip()

            if part:
                parts.append(part)

        if not parts:
            return ""

        body = "\n\n".join(p.strip() for p in parts) + "\n"
        return self._rewrite_relative_image_refs(body, folder_name)

    def _rewrite_relative_image_refs(self, content: str, folder_name: str) -> str:
        """Rewrite relative image refs to their served assets path."""
        def rewrite(m: re.Match) -> str:
            alt, src = m.group(1), m.group(2)
            if src.startswith(('http://', 'https://', '/')):
                return m.group(0)
            return f'![{alt}](/assets/results/{folder_name}/{src})'
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', rewrite, content)

    def _copy_folder_assets(self, folder: Path):
        """Copy non-CSV/MD files (images, etc.) to assets/results/{folder}/ for Jekyll to serve."""
        asset_files = [
            f for f in folder.iterdir()
            if f.is_file()
            and f.name != '_frontmatter.md'
            and f.suffix not in ('.csv', '.md')
        ]
        if not asset_files:
            return

        dest_dir = self.assets_dir / folder.name
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        dest_dir.mkdir(parents=True)

        for asset in asset_files:
            shutil.copy2(asset, dest_dir / asset.name)
            self.logger.info(f"Copied asset: {asset.name} → assets/results/{folder.name}/")

    def _csv_to_table(self, csv_path: Path) -> str:
        rows = self.csv_reader.read(csv_path)

        if not rows:
            self.logger.info(f"Empty CSV: {csv_path.name}")
            return "*No data available*"

        headers = rows[0]
        data_rows = rows[1:]
        self._validate_table_structure(data_rows, headers, csv_path)
        table = self.table_formatter.format(rows)
        self.logger.success(f"Generated table from {csv_path.name} ({len(data_rows)} row(s))")
        return table

    def _validate_table_structure(self, data_rows: list[list[str]],
                                  headers: list[str], csv_path: Path):
        if inconsistent := self.table_validator.validate(data_rows, headers):
            raise ValueError(
                f"Inconsistent column count in rows: {inconsistent}\n"
                f"\tExpected {len(headers)} column(s) to match headers: {', '.join(headers)}\n"
                f"\tCheck that all data rows have the same number of columns as the header row."
            )

    def _write_post(self, folder: Path, content: str, file_date: str) -> Path:
        filename = self.filename_generator.generate(file_date, folder.name)
        output_path = self.posts_dir / filename
        self.post_writer.write(output_path, content)
        return output_path

    # -------------------------------------------------------------------------
    # Output directory management
    # -------------------------------------------------------------------------

    def _ensure_output_dirs(self):
        self._clean_output_dir()
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.logger.success(f"Output directory ready: {self.posts_dir}")

    def _clean_output_dir(self):
        if self.posts_dir.exists():
            for file in self.posts_dir.glob("*.md"):
                file.unlink()
                self.logger.info(f"Removed old file: {file.name}")

    # -------------------------------------------------------------------------
    # Logging helpers
    # -------------------------------------------------------------------------

    def _log_date_info(self, fm: dict, date_str: str):
        if 'date' not in fm:
            self.logger.info(f"No date found, using today: {date_str}")

    def _log_folder_error(self, folder: Path, error: Exception):
        if isinstance(error, ValueError):
            self._log_validation_error(folder, error)
        else:
            self._log_unexpected_error(folder, error)

    def _log_validation_error(self, folder: Path, error: ValueError):
        self.logger.error(f"VALIDATION ERROR in folder '{folder.name}'")
        self.logger.error(f"\t{error}")
        self.logger.info(f"\tFix the issue in _fencing-results/{folder.name}/ and try again.")

    def _log_unexpected_error(self, folder: Path, error: Exception):
        self.logger.error(f"UNEXPECTED ERROR in folder '{folder.name}'")
        self.logger.error(f"\t{type(error).__name__}: {error}")
        self.logger.info(f"\tThis may be a bug. Check _fencing-results/{folder.name}/ for issues.")

    def _print_error_summary(self, errors: list[tuple[str, str]]):
        self.logger.header(f"FAILED: {len(errors)} folder(s) had errors")
        for folder_name, error in errors:
            self.logger.error(f"- {folder_name}: {error}")
        self.logger.info("Fix the errors above and commit again.")
        self.logger.warning("The deployment has been blocked to prevent broken content.")

    def _print_summary(self, count: int):
        self.logger.header(f"\u2713 Successfully generated {count} result post(s)")
        self.logger.info("Posts: _posts/results/ (gitignored)")
        self.logger.info("Results appear on homepage and /news/ feed")


if __name__ == "__main__":
    generator = ResultsGenerator()
    generator.run()
