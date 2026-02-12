"""CSV loader for test booklet item metadata."""

from pathlib import Path

import polars as pl

from generator.booklets import Booklet, BookletKey, Item


def _parse_float(value: str | float | int | None) -> float:
    """Parse a numeric value that may be a string with comma decimal separator."""
    if value is None:
        return 0.0
    if isinstance(value, str):
        if value == "":
            return 0.0
        return float(value.replace(",", "."))
    return float(value)


def _parse_optional_float(value: str | float | int | None) -> float | None:
    """Parse a numeric value, returning None for missing data."""
    if value is None:
        return None
    if isinstance(value, str):
        if value == "":
            return None
        return float(value.replace(",", "."))
    return float(value)


def load_items_from_csv(csv_path: Path) -> pl.DataFrame:
    """Load raw item data from a CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        Polars DataFrame with item data
    """
    return pl.read_csv(
        csv_path,
        separator=";",
        encoding="latin1",
        null_values=[""],
    )


_REQUIRED_COLUMNS = {
    "vera",
    "tjahr",
    "fach",
    "iqbtestheft_id",
    "iqbitem_id",
    "name",
    "kstufe",
    "itemnr_th",
}


def build_booklets_from_dataframe(df: pl.DataFrame) -> dict[BookletKey, Booklet]:
    """Build Booklet objects from a DataFrame.

    Args:
        df: DataFrame with item data (columns: vera, tjahr, fach, iqbtestheft_id, etc.)

    Returns:
        Dictionary mapping BookletKey to Booklet objects

    Raises:
        ValueError: If the DataFrame is missing required columns.
    """
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required column(s): {sorted(missing)}")

    # Only include rows where model is null or "global" to avoid
    # duplicates from different models
    if "model" in df.columns:
        df = df.filter(pl.col("model").is_null() | (pl.col("model") == "global"))

    booklets: dict[BookletKey, Booklet] = {}

    for row in df.iter_rows(named=True):
        level = int(row["vera"])
        year = int(row["tjahr"])
        subject = str(row["fach"])
        booklet_id = str(row["iqbtestheft_id"])

        key = BookletKey(level=level, year=year, subject=subject, booklet_id=booklet_id)

        if key not in booklets:
            booklets[key] = Booklet(key=key)

        item_order = _parse_float(row.get("itemord_th"))
        logit = _parse_float(row.get("logit"))
        bista = _parse_float(row.get("bista"))

        # Parse domain
        domain_raw = row.get("domain")
        domain = str(domain_raw) if domain_raw is not None else None

        item = Item(
            iqbitem_id=str(row["iqbitem_id"]),
            name=str(row["name"]),
            logit=logit,
            bista=bista,
            competence_level=str(row["kstufe"]),
            domain=domain,
            item_nr_booklet=str(row["itemnr_th"]),
            item_order_booklet=item_order,
            solution_freq_primary_school=_parse_optional_float(row.get("lh_gs")),
            solution_freq_gymnasium=_parse_optional_float(row.get("lh_gy")),
            solution_freq_non_gymnasium=_parse_optional_float(row.get("lh_ng")),
        )

        booklets[key].items.append(item)

    return booklets


def load_booklets_from_csv(csv_path: Path) -> dict[BookletKey, Booklet]:
    """Load booklets from a single CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        Dictionary mapping BookletKey to Booklet objects
    """
    df = load_items_from_csv(csv_path)
    return build_booklets_from_dataframe(df)


def load_booklets_from_directory(
    directory: Path, pattern: str = "*.csv"
) -> dict[BookletKey, Booklet]:
    """Load booklets from all CSV files in a directory.

    Args:
        directory: Path to directory containing CSV files
        pattern: Glob pattern for CSV files

    Returns:
        Dictionary mapping BookletKey to Booklet objects (merged from all files)
    """
    all_booklets: dict[BookletKey, Booklet] = {}

    for csv_path in directory.glob(pattern):
        booklets = load_booklets_from_csv(csv_path)
        for key, booklet in booklets.items():
            if key in all_booklets:
                # Merge items from the same booklet across files
                all_booklets[key].items.extend(booklet.items)
            else:
                all_booklets[key] = booklet

    return all_booklets
