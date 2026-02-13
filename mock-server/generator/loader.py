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


def _parse_optional_str(value: str | float | int | None) -> str | None:
    """Parse a value as a stripped string, returning None for missing data."""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _parse_flag(value: str | float | int | None) -> bool:
    """Parse a boolean flag column (1 or null → True/False)."""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() == "1"
    return int(value) == 1


def _collect_flags(
    row: dict[str, object], columns: tuple[str, ...]
) -> list[str] | None:
    """Collect column names where the flag value is 1.

    Returns None if no columns have a positive flag.
    Only columns present in the row are checked.
    """
    result = [col for col in columns if col in row and _parse_flag(row[col])]
    return result if result else None


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

        # Parse competence_standard from kompstd1/2/3
        kompstd_list = [
            v
            for col in ("kompstd1", "kompstd2", "kompstd3")
            if (v := _parse_optional_str(row.get(col))) is not None
        ]
        competence_standard = kompstd_list if kompstd_list else None

        # Parse listening_or_reading_style from boolean flag columns.
        # Handle CSV spelling inconsistency: "detailliert" vs "detailiert"
        _style_mapping: dict[str, str] = {
            "selektiv": "selektiv",
            "detailliert": "detailliert",
            "detailiert": "detailliert",
            "inferierend": "inferierend",
            "global": "global",
        }
        listening_or_reading_style: str | None = None
        for csv_col, canonical in _style_mapping.items():
            if csv_col in row and _parse_flag(row[csv_col]):
                listening_or_reading_style = canonical
                break

        # Parse general_mathematical_competence from K1-K6 and A1-A5 flags
        general_mathematical_competence = _collect_flags(
            row, ("K1", "K2", "K3", "K4", "K5", "K6", "A1", "A2", "A3", "A4", "A5")
        )

        # Parse core_idea from L1-L5 flags
        core_idea = _collect_flags(row, ("L1", "L2", "L3", "L4", "L5"))

        # Parse cognitive_demand_level from AFB column
        afb_raw = row.get("AFB")
        cognitive_demand_level = str(int(afb_raw)) if afb_raw is not None else None

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
            competence_standard=competence_standard,
            listening_or_reading_style=listening_or_reading_style,
            general_mathematical_competence=general_mathematical_competence,
            core_idea=core_idea,
            cognitive_demand_level=cognitive_demand_level,
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
