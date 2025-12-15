#!/usr/bin/env python3
"""
Integration tests for convert_fencing_results.py

Tests the complete flow from CSV inputs to generated markdown posts,
covering various frontmatter and content scenarios.

All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add _scripts directory to path to import convert_fencing_results
_scripts_dir = Path(__file__).parent.parent / "_scripts"
sys.path.insert(0, str(_scripts_dir))

from convert_fencing_results import ResultsGenerator  # noqa: E402


@pytest.fixture
def test_env():
    """Create temporary test environment with source and output directories."""
    test_dir = Path(tempfile.mkdtemp())
    source_dir = test_dir / "_fencing-results"
    posts_dir = test_dir / "_posts" / "results"
    source_dir.mkdir(parents=True)
    posts_dir.mkdir(parents=True)
    
    # Path to test fixtures
    fixtures_dir = Path(__file__).parent / "fixtures"
    
    env = {
        'test_dir': test_dir,
        'source_dir': source_dir,
        'posts_dir': posts_dir,
        'fixtures_dir': fixtures_dir,
    }
    
    yield env
    
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def generator(test_env):
    """Create a ResultsGenerator pointed at test directories."""
    gen = ResultsGenerator()
    gen.source_dir = test_env['source_dir']
    gen.posts_dir = test_env['posts_dir']
    gen.project_root = test_env['test_dir']
    return gen


def copy_fixture(test_env, fixture_name: str, dest_name: str = None):
    """Copy a fixture file (CSV or MD) to the test source directory.
    
    If fixture_name has an extension, uses it directly.
    Otherwise tries both .csv and .md extensions and copies both if they exist.
    """
    if dest_name is None:
        dest_name = fixture_name
    
    # If explicit extension provided
    if '.' in fixture_name:
        src = test_env['fixtures_dir'] / fixture_name
        if src.exists():
            dest = test_env['source_dir'] / (dest_name if '.' in dest_name else f"{dest_name}{src.suffix}")
            shutil.copy(src, dest)
            return
        raise FileNotFoundError(f"Fixture not found: {fixture_name}")
    
    # No extension - try both CSV and MD
    copied = False
    for ext in ['.csv', '.md']:
        src = test_env['fixtures_dir'] / f"{fixture_name}{ext}"
        if src.exists():
            dest = test_env['source_dir'] / f"{dest_name}{ext}"
            shutil.copy(src, dest)
            copied = True
    
    if not copied:
        raise FileNotFoundError(f"No fixtures found for: {fixture_name}")


class TestResultsGeneration:
    """Integration tests for CSV-to-markdown post generation."""
    
    def test_csv_only_no_frontmatter(self, test_env, generator):
        """Test: CSV file only, no .md file - should use defaults."""
        # Arrange
        copy_fixture(test_env, "basic-tournament", "test-tournament-2025")
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1, "Should generate exactly one post"
        
        output_content = output_files[0].read_text()
        
        # Verify default frontmatter generated
        assert "layout: post" in output_content
        assert "Test Tournament 2025" in output_content
        assert datetime.now().strftime('%Y-%m-%d') in output_content
        
        # Verify table content rendered correctly
        assert "| Fencer | Score |" in output_content
        assert "| Smith John | 450 |" in output_content
        assert "| Doe Jane | 425 |" in output_content
    
    def test_csv_with_frontmatter_no_intro(self, test_env, generator):
        """Test: CSV with .md file containing only frontmatter."""
        # Arrange
        copy_fixture(test_env, "spring-open", "spring-open-2025")
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1
        
        output_content = output_files[0].read_text()
        
        # Verify custom frontmatter used instead of defaults
        assert 'title: "Spring Open Championship"' in output_content
        assert 'date: 2025-03-15' in output_content
        assert 'excerpt: "Championship results"' in output_content
        assert 'author: "Tournament Director"' in output_content
        
        # Verify table generated
        assert "| Fencer | Score |" in output_content
        assert "| Anderson Alex | 500 |" in output_content
        
        # Verify filename uses date from frontmatter
        assert output_files[0].name == "2025-03-15-spring-open-2025.md"
    
    def test_csv_with_frontmatter_and_intro(self, test_env, generator):
        """Test: CSV with .md containing frontmatter AND intro content."""
        # Arrange
        copy_fixture(test_env, "winter-classic", "winter-classic-2025")
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        output_content = output_files[0].read_text()
        
        # Verify frontmatter with datetime
        assert 'title: "Winter Classic 2025"' in output_content
        assert 'date: "2025-12-20 14:30:00"' in output_content
        
        # Verify intro content appears
        assert "The Winter Classic featured 24 fencers" in output_content
        assert "Congratulations to all participants!" in output_content
        
        # Verify intro comes BEFORE table
        intro_pos = output_content.find("The Winter Classic")
        table_pos = output_content.find("| Fencer | Wins | Losses |")
        assert intro_pos < table_pos, "Intro must appear before table"
        
        # Verify filename uses date part only (not time)
        assert output_files[0].name == "2025-12-20-winter-classic-2025.md"
    
    def test_inconsistent_column_count(self, test_env, generator):
        """Test: CSV with inconsistent column counts - should handle gracefully."""
        # Arrange
        copy_fixture(test_env, "inconsistent-columns", "inconsistent-2025")
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 1, "Should not crash on inconsistent columns"
        
        output_content = output_files[0].read_text()
        
        # Verify table created with proper padding/truncation
        assert "| Name | Score | Rank |" in output_content
        assert "| Alice | 100 | 1 |" in output_content
        assert "| Bob | 95 |  |" in output_content  # Padded with empty cell
        assert "| Charlie | 90 | 3 |" in output_content  # Extra column truncated
    
    def test_empty_csv(self, test_env, generator):
        """Test: Empty CSV file - should handle gracefully."""
        # Arrange
        copy_fixture(test_env, "empty", "empty-2025")
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        output_content = output_files[0].read_text()
        
        # Verify default frontmatter generated
        assert "layout: post" in output_content
        
        # Verify "no data" message instead of crash
        assert "*No data available*" in output_content
    
    def test_csv_with_bom(self, test_env, generator):
        """Test: CSV with UTF-8 BOM - should strip it from headers."""
        # Arrange
        csv_path = test_env['source_dir'] / "bom-test-2025.csv"
        csv_path.write_text("\ufeffFencer,Points\nRoberts Robin,525\n", encoding='utf-8')
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        output_content = output_files[0].read_text()
        
        # Verify BOM stripped from header
        assert "| Fencer | Points |" in output_content
        assert "\ufeff" not in output_content, "BOM should be stripped"
    
    @pytest.mark.parametrize("num_files", [1, 3, 5])
    def test_multiple_csv_files(self, test_env, generator, num_files):
        """Test: Multiple CSV files - should generate multiple posts."""
        # Arrange
        for i in range(num_files):
            csv_content = f"Fencer,Score\nTest{i},{100 + i}\n"
            csv_path = test_env['source_dir'] / f"tournament-{i}-2025.csv"
            csv_path.write_text(csv_content)
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == num_files, f"Should generate {num_files} posts"
        
        # Verify each has proper structure
        for output_file in output_files:
            content = output_file.read_text()
            assert "layout: post" in content
            assert "| Fencer | Score |" in content
    
    def test_frontmatter_with_special_characters(self, test_env, generator):
        """Test: Frontmatter with colons and quotes - should escape properly."""
        # Arrange
        copy_fixture(test_env, "special-chars", "special-2025")
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        output_content = output_files[0].read_text()
        
        # Verify values with colons are properly quoted
        assert 'title: "Tournament: The Finals"' in output_content
        assert 'excerpt: "Winner\'s bracket: Gold medal round"' in output_content


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_no_source_directory(self, test_env):
        """Test: No source directory exists - should handle gracefully."""
        # Arrange
        generator = ResultsGenerator()
        generator.source_dir = test_env['test_dir'] / "nonexistent"
        generator.posts_dir = test_env['posts_dir']
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 0, "Should not generate posts when source missing"
    
    def test_no_csv_files(self, test_env, generator):
        """Test: Source directory exists but has no CSV files."""
        # Arrange
        # (source_dir already exists but is empty)
        
        # Act
        generator.run()
        
        # Assert
        output_files = list(test_env['posts_dir'].glob("*.md"))
        assert len(output_files) == 0, "Should not generate posts when no CSVs found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
