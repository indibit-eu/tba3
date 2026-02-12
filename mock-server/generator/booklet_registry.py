"""Booklet registry for centralized access to test booklets."""

from pathlib import Path

from generator.booklets import Booklet, BookletKey
from generator.loader import load_booklets_from_directory


class BookletRegistry:
    """Central registry for managing test booklets."""

    def __init__(self) -> None:
        self._booklets: dict[BookletKey, Booklet] = {}

    def load_from_directory(
        self, directory: Path, pattern: str = "*.csv"
    ) -> BookletRegistry:
        """Load booklets from CSV files in a directory.

        Args:
            directory: Path to directory containing CSV files
            pattern: Glob pattern for CSV files

        Returns:
            Self for method chaining
        """
        booklets = load_booklets_from_directory(directory, pattern)
        self._booklets.update(booklets)
        return self

    def get(self, key: BookletKey) -> Booklet | None:
        """Get a booklet by its key.

        Args:
            key: The unique booklet key

        Returns:
            The booklet if found, None otherwise
        """
        return self._booklets.get(key)

    @property
    def count(self) -> int:
        """Return the number of registered booklets."""
        return len(self._booklets)
