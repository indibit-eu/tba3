"""Data models for test booklets and items."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BookletKey:
    """Unique identifier for a test booklet."""

    level: int
    year: int
    subject: str
    booklet_id: str

    def __str__(self) -> str:
        return f"V{self.level}-{self.year}-{self.subject.upper()}-{self.booklet_id}"

    @classmethod
    def from_str(cls, s: str) -> BookletKey:
        """Parse a BookletKey string like 'V3-2024-DE-TH01'.

        The format is V{level}-{year}-{subject}-{booklet_id}.
        The booklet_id may contain dashes, so only the first 3 segments
        are fixed; the rest is the booklet_id.

        Args:
            s: BookletKey string to parse

        Returns:
            Parsed BookletKey with lowercased subject

        Raises:
            ValueError: If the string cannot be parsed
        """
        parts = s.split("-")
        if len(parts) < 4:
            raise ValueError(
                f"BookletKey must have at least 4 dash-separated segments, "
                f"got {len(parts)}: '{s}'"
            )

        level_str = parts[0]
        if not level_str.startswith("V"):
            raise ValueError(f"BookletKey must start with 'V', got: '{level_str}'")
        try:
            level = int(level_str[1:])
        except ValueError as e:
            raise ValueError(f"Cannot parse level from '{level_str}'") from e

        try:
            year = int(parts[1])
        except ValueError as e:
            raise ValueError(f"Cannot parse year from '{parts[1]}'") from e

        subject = parts[2].lower()
        booklet_id = "-".join(parts[3:])
        if not booklet_id:
            raise ValueError("Booklet ID is empty")

        return cls(level=level, year=year, subject=subject, booklet_id=booklet_id)


@dataclass(frozen=True)
class DomainKey:
    """Unique identifier for a domain."""

    subject: str
    domain: str | None

    def __str__(self) -> str:
        if self.domain:
            return f"{self.subject.upper()}-{self.domain}"
        return self.subject.upper()


@dataclass
class Item:
    """A single test item

    Attributes:
        iqbitem_id: Unique IQB item identifier (e.g., "D38701", "M1674501")
        name: Human-readable item/stimulus name
        logit: Item difficulty in logits (IRT parameter)
        bista: BISTA scale score (transformed difficulty)
        competence_level: Assigned competence level (e.g. "I", "Ia", "IV", "A2.1", ...)
        domain: Content domain (e.g., "le", "ho", "rs", "gm")
        item_nr_booklet: Item number within the booklet (e.g., "1.1")
        item_order_booklet: Numeric order in booklet for sorting
    """

    iqbitem_id: str
    name: str
    logit: float
    bista: float
    competence_level: str
    domain: str | None
    item_nr_booklet: str
    item_order_booklet: float
    solution_freq_primary_school: float | None = None
    solution_freq_gymnasium: float | None = None
    solution_freq_non_gymnasium: float | None = None

    @property
    def column_name(self) -> str:
        """DataFrame column name for this item's response data."""
        return f"item_{self.iqbitem_id}"


@dataclass
class Booklet:
    """A test booklet containing multiple items.

    Attributes:
        key: Unique booklet identifier
        items: List of items in this booklet, ordered by item_order_booklet
    """

    key: BookletKey
    items: list[Item] = field(default_factory=list)

    @property
    def level(self) -> int:
        """Test VERA level."""
        return self.key.level

    @property
    def year(self) -> int:
        """Test year."""
        return self.key.year

    @property
    def subject(self) -> str:
        """Test subject."""
        return self.key.subject

    @property
    def booklet_id(self) -> str:
        """Booklet ID (e.g., TH01)."""
        return self.key.booklet_id

    @property
    def item_count(self) -> int:
        """Number of items in this booklet."""
        return len(self.items)

    def get_items_sorted(self) -> list[Item]:
        """Return items sorted by their order in the booklet."""
        return sorted(self.items, key=lambda item: item.item_order_booklet)

    def get_domains(self) -> set[str]:
        """Return all domains covered by items in this booklet."""
        return {item.domain for item in self.items if item.domain is not None}

    def items_by_domain(self) -> dict[str | None, list[Item]]:
        """Group items by their domain. None key for domain-less items."""
        result: dict[str | None, list[Item]] = {}
        for item in self.items:
            result.setdefault(item.domain, []).append(item)
        return result

    def column_names_for_domain(self, domain: str | None) -> list[str]:
        """Return item column names, optionally filtered by domain.

        Args:
            domain: If not None, only include items matching this domain.
                If None, include all items.
        """
        if domain is not None:
            items = [i for i in self.items if i.domain == domain]
        else:
            items = self.items
        return [item.column_name for item in items]
