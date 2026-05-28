#!/usr/bin/env python3
"""
Integration tests for convert_fencing_results.py

Tests the complete flow from folder-based inputs to generated markdown posts.
Each result folder contains _frontmatter.md (required) plus optional CSV/MD files.

All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
import shutil
from pathlib import Path
import sys

# Add _scripts directory to path
_scripts_dir = Path(__file__).parent.parent / "_scripts"
sys.path.insert(0, str(_scripts_dir))

from convert_fencing_results import ResultsGenerator  # noqa: E402


@pytest.fixture
def test_env(tmp_path):
    """Create temporary test environment with source and output directories."""
    source_dir = tmp_path / "_fencing-results"
    posts_dir = tmp_path / "_posts" / "results"
    source_dir.mkdir(parents=True)
    posts_dir.mkdir(parents=True)

    fixtures_dir = Path(__file__).parent / "fixtures"

    yield {
        'test_dir': tmp_path,
        'source_dir': source_dir,
        'posts_dir': posts_dir,
        'fixtures_dir': fixtures_dir,
    }


@pytest.fixture
def generator(test_env):
    """Create a ResultsGenerator pointed at test directories."""
    gen = ResultsGenerator()
    gen.source_dir = test_env['source_dir']
    gen.posts_dir = test_env['posts_dir']
    gen.project_root = test_env['test_dir']
    gen.assets_dir = test_env['test_dir'] / "assets" / "results"
    return gen


def copy_fixture_folder(test_env, fixture_folder_name: str, dest_folder_name: str = None):
    """Copy a fixture directory into the test source directory."""
    if dest_folder_name is None:
        dest_folder_name = fixture_folder_name

    src = test_env['fixtures_dir'] / fixture_folder_name
    dest = test_env['source_dir'] / dest_folder_name
    shutil.copytree(src, dest)


class TestFolderBasedGeneration:
    """Tests for the core folder-based post generation."""

    def test_basic_folder_generates_post(self, test_env, generator):
        """Folder with _frontmatter.md and CSV produces a post."""
        copy_fixture_folder(test_env, "basic-tournament")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1, "Should generate exactly one post"

        content = output_files[0].read_text()
        assert "layout: post" in content
        assert "Basic Tournament" in content
        assert "date: 2025-01-01" in content
        assert "| Fencer | Score |" in content
        assert "| Smith John | 450 |" in content
        assert "| Doe Jane | 425 |" in content
        assert output_files[0].name == "2025-01-01-basic-tournament.md"

    def test_folder_with_custom_frontmatter(self, test_env, generator):
        """Folder with rich _frontmatter.md uses all provided fields."""
        copy_fixture_folder(test_env, "spring-open")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1

        content = output_files[0].read_text()
        assert 'title: "Spring Open Championship"' in content
        assert 'date: 2025-03-15' in content
        assert 'excerpt: "Championship results"' in content
        assert 'author: "Tournament Director"' in content
        assert "| Fencer | Score |" in content
        assert "| Anderson Alex | 500 |" in content
        assert output_files[0].name == "2025-03-15-spring-open.md"

    def test_folder_with_intro_md_and_csv(self, test_env, generator):
        """Folder with separate intro.md and results.csv stitches content in alpha order."""
        copy_fixture_folder(test_env, "winter-classic")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        content = output_files[0].read_text()

        assert 'title: "Winter Classic 2025"' in content
        assert 'date: "2025-12-20 14:30:00"' in content
        assert "The Winter Classic featured 24 fencers" in content
        assert "Congratulations to all participants!" in content
        assert "| Fencer | Wins | Losses |" in content

        # intro.md ('i') sorts before results.csv ('r'), so intro appears first
        intro_pos = content.find("The Winter Classic featured")
        table_pos = content.find("| Fencer | Wins | Losses |")
        assert intro_pos < table_pos, "Intro content must appear before the table"
        assert output_files[0].name == "2025-12-20-winter-classic.md"

    def test_frontmatter_body_appears_first(self, test_env, generator):
        """Body text in _frontmatter.md appears before all other content files."""
        copy_fixture_folder(test_env, "multiple-content-files")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        content = output_files[0].read_text()

        assert "Content from frontmatter body" in content
        assert "First alphabetical MD content" in content
        assert "| Fencer | Score |" in content
        assert "Last alphabetical MD content" in content

        fm_body_pos = content.find("Content from frontmatter body")
        aaa_pos = content.find("First alphabetical MD content")
        table_pos = content.find("| Fencer | Score |")
        zzz_pos = content.find("Last alphabetical MD content")

        assert fm_body_pos < aaa_pos, "Frontmatter body must come before aaa-intro.md"
        assert aaa_pos < table_pos, "aaa-intro.md must come before bbb-results.csv table"
        assert table_pos < zzz_pos, "bbb-results.csv table must come before zzz-closing.md"

    def test_multiple_folders_generate_multiple_posts(self, test_env, generator):
        """Multiple result folders each produce their own post."""
        copy_fixture_folder(test_env, "basic-tournament", "tournament-a")
        copy_fixture_folder(test_env, "spring-open", "tournament-b")
        copy_fixture_folder(test_env, "winter-classic", "tournament-c")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 3, "Should generate one post per folder"

    def test_root_level_files_are_ignored(self, test_env, generator):
        """CSV and MD files at the root of _fencing-results/ are silently ignored."""
        copy_fixture_folder(test_env, "basic-tournament")
        (test_env['source_dir'] / "stray-file.csv").write_text("Fencer,Score\nIgnore Me,999\n")
        (test_env['source_dir'] / "README.md").write_text("# Instructions\n")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1
        content = output_files[0].read_text()
        assert "Ignore Me" not in content

    def test_non_csv_non_md_files_ignored(self, test_env, generator):
        """Image files and other non-CSV/MD files inside a folder are silently ignored."""
        copy_fixture_folder(test_env, "basic-tournament")
        folder = test_env['source_dir'] / "basic-tournament"
        (folder / "photo.png").write_bytes(b"\x89PNG\r\n")
        (folder / "notes.txt").write_text("some notes")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1

    def test_image_references_in_markdown_rewritten_and_assets_copied(self, test_env, generator):
        """Relative image refs are rewritten to /assets/results/{folder}/ and files are copied there."""
        folder = test_env['source_dir'] / "photo-tournament"
        folder.mkdir()
        (folder / "_frontmatter.md").write_text(
            "---\ntitle: Photo Tournament\ndate: 2026-05-01\n---\n"
        )
        (folder / "intro.md").write_text(
            "Great action at the tournament!\n\n"
            "![Trophy ceremony](trophy.jpg)\n\n"
            "See also: ![Group photo](group-photo.png)\n"
        )
        (folder / "trophy.jpg").write_bytes(b"\xff\xd8\xff")      # fake JPEG
        (folder / "group-photo.png").write_bytes(b"\x89PNG\r\n")  # fake PNG
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1
        content = output_files[0].read_text()

        # Refs must be rewritten to absolute paths Jekyll can serve
        assert "![Trophy ceremony](/assets/results/photo-tournament/trophy.jpg)" in content
        assert "![Group photo](/assets/results/photo-tournament/group-photo.png)" in content
        assert "Great action at the tournament!" in content

        # Raw relative refs must NOT remain
        assert "](trophy.jpg)" not in content
        assert "](group-photo.png)" not in content

        # Asset files must be copied to the assets directory
        assets_dir = test_env['test_dir'] / "assets" / "results" / "photo-tournament"
        assert (assets_dir / "trophy.jpg").exists()
        assert (assets_dir / "group-photo.png").exists()

    def test_absolute_and_external_image_refs_not_rewritten(self, test_env, generator):
        """Absolute paths and external URLs in image refs are left unchanged."""
        folder = test_env['source_dir'] / "link-test"
        folder.mkdir()
        (folder / "_frontmatter.md").write_text(
            "---\ntitle: Link Test\ndate: 2026-05-01\n---\n"
        )
        (folder / "content.md").write_text(
            "![External](https://example.com/img.jpg)\n"
            "![Absolute](/assets/shared/logo.png)\n"
            "![Relative](local.jpg)\n"
        )
        (folder / "local.jpg").write_bytes(b"\xff\xd8\xff")
        generator.run()

        content = output_files = list(test_env['posts_dir'].glob("*.md"))[0].read_text()
        assert "![External](https://example.com/img.jpg)" in content
        assert "![Absolute](/assets/shared/logo.png)" in content
        assert "![Relative](/assets/results/link-test/local.jpg)" in content

    def test_output_filename_uses_folder_name_and_date(self, test_env, generator):
        """Output filename is {date}-{folder-name}.md using date from _frontmatter.md."""
        copy_fixture_folder(test_env, "spring-open", "my-tournament-2025")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert output_files[0].name == "2025-03-15-my-tournament-2025.md"

    def test_folder_with_only_frontmatter_generates_post(self, test_env, generator):
        """A folder with just _frontmatter.md (no content files) generates a valid post."""
        folder = test_env['source_dir'] / "empty-post"
        folder.mkdir()
        (folder / "_frontmatter.md").write_text("---\ntitle: Empty Post\ndate: 2025-05-01\n---\n")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1
        content = output_files[0].read_text()
        assert "layout: post" in content
        assert "Empty Post" in content

    def test_datetime_uses_date_part_for_filename(self, test_env, generator):
        """A date+time value uses only the date portion for the output filename."""
        copy_fixture_folder(test_env, "winter-classic")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert output_files[0].name == "2025-12-20-winter-classic.md"

    def test_empty_csv_produces_no_data_message(self, test_env, generator):
        """An empty CSV renders a no-data message rather than crashing."""
        copy_fixture_folder(test_env, "empty-csv")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        content = output_files[0].read_text()
        assert "layout: post" in content
        assert "*No data available*" in content

    def test_bom_csv_header_stripped(self, test_env, generator):
        """A CSV with a UTF-8 BOM has the BOM stripped from the header row."""
        copy_fixture_folder(test_env, "bom-test")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        content = output_files[0].read_text()
        assert "| Fencer | Points |" in content
        assert "\ufeff" not in content, "BOM should be stripped from output"

    def test_special_characters_in_frontmatter_escaped(self, test_env, generator):
        """Frontmatter values containing colons or quotes are properly quoted."""
        copy_fixture_folder(test_env, "special-chars")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        content = output_files[0].read_text()
        assert 'title: "Tournament: The Finals"' in content
        assert "excerpt: \"Winner's bracket: Gold medal round\"" in content

    @pytest.mark.parametrize("num_folders", [1, 3, 5])
    def test_n_folders_produce_n_posts(self, test_env, generator, num_folders):
        """Exactly one post is generated per result folder."""
        for i in range(num_folders):
            folder = test_env['source_dir'] / f"tournament-{i}"
            folder.mkdir()
            (folder / "_frontmatter.md").write_text(
                f"---\ntitle: Tournament {i}\ndate: 2025-0{(i % 9) + 1}-01\n---\n"
            )
            (folder / "results.csv").write_text(f"Fencer,Score\nPlayer{i},{100 + i}\n")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == num_folders


class TestFolderValidation:
    """Tests that invalid folders fail hard with clear errors."""

    def test_folder_without_frontmatter_fails(self, test_env, generator, capsys):
        """A folder without _frontmatter.md causes SystemExit(1)."""
        copy_fixture_folder(test_env, "no-frontmatter")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "no-frontmatter" in captured.out
        assert "_frontmatter.md" in captured.out

    def test_frontmatter_missing_title_fails(self, test_env, generator, capsys):
        """A _frontmatter.md without title causes SystemExit(1)."""
        copy_fixture_folder(test_env, "missing-title")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "missing-title" in captured.out
        assert "title" in captured.out

    def test_frontmatter_missing_date_fails(self, test_env, generator, capsys):
        """A _frontmatter.md without date causes SystemExit(1)."""
        copy_fixture_folder(test_env, "missing-date")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "missing-date" in captured.out
        assert "date" in captured.out

    def test_frontmatter_bad_date_format_fails(self, test_env, generator, capsys):
        """An invalid date in _frontmatter.md causes SystemExit(1) with a clear message."""
        copy_fixture_folder(test_env, "bad-date")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "VALIDATION ERROR" in captured.out
        assert "bad-date" in captured.out
        assert "Invalid date format" in captured.out
        assert "2025-13-45" in captured.out
        assert "Expected format: YYYY-MM-DD" in captured.out

    def test_inconsistent_csv_columns_fails(self, test_env, generator):
        """A CSV with inconsistent row lengths causes SystemExit(1)."""
        copy_fixture_folder(test_env, "inconsistent-columns")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1

    def test_mismatched_csv_column_count_fails(self, test_env, generator, capsys):
        """A CSV row with more columns than headers causes SystemExit(1) with details."""
        copy_fixture_folder(test_env, "mismatched-header-vs-row-length")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "VALIDATION ERROR" in captured.out
        assert "mismatched-header-vs-row-length" in captured.out
        assert "Inconsistent column count" in captured.out
        assert "Expected 2 column(s)" in captured.out
        assert "Fencer, Score" in captured.out

    def test_garbage_file_fails(self, test_env, generator, capsys):
        """A CSV that is actually garbage text causes SystemExit(1)."""
        copy_fixture_folder(test_env, "garbage")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "garbage" in captured.out
        assert ("ERROR" in captured.out or "error" in captured.out)

    def test_unconverted_xls_fails(self, test_env, generator, capsys):
        """A file that is really XLS disguised as CSV causes SystemExit(1)."""
        copy_fixture_folder(test_env, "unconverted-xls")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "unconverted-xls" in captured.out
        assert ("File encoding error" in captured.out or "Malformed CSV" in captured.out)

    def test_multiple_folders_one_invalid_collects_all_errors(self, test_env, generator, capsys):
        """All folders are attempted; errors accumulate before final failure."""
        copy_fixture_folder(test_env, "basic-tournament", "good-a")
        copy_fixture_folder(test_env, "spring-open", "good-b")
        copy_fixture_folder(test_env, "bad-date")

        with pytest.raises(SystemExit) as exc_info:
            generator.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "FAILED: 1 folder(s) had errors" in captured.out
        assert "bad-date" in captured.out
        assert "Invalid date format" in captured.out

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 2, "Good folders should still produce posts"


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_no_source_directory(self, test_env):
        """Missing source directory produces no posts and no error."""
        generator = ResultsGenerator()
        generator.source_dir = test_env['test_dir'] / "nonexistent"
        generator.posts_dir = test_env['posts_dir']
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 0

    def test_empty_source_directory(self, test_env, generator):
        """Source directory with no subdirectories produces no posts."""
        (test_env['source_dir'] / "README.md").write_text("# README\n")
        generator.run()

        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 0

    def test_existing_posts_cleaned_before_regeneration(self, test_env, generator):
        """Stale posts in _posts/results/ are removed before new generation."""
        stale = test_env['posts_dir'] / "2020-01-01-old-post.md"
        stale.write_text("old content")
        copy_fixture_folder(test_env, "basic-tournament")
        generator.run()

        assert not stale.exists(), "Stale post should be removed"
        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
