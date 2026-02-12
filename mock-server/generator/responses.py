"""Item response generation with deterministic noise using NumPy matrices."""

import zlib

import numpy as np
import polars as pl

from generator.booklets import Booklet


def generate_item_responses(
    students: pl.DataFrame,
    booklet: Booklet,
    seed: str,
) -> pl.DataFrame:
    """Generate item responses for all students on a booklet.

    Uses IRT 1PL model with deterministic seed-based noise for reproducible
    but slightly varying scores. Computation is vectorized using NumPy matrices.

    Args:
        students: DataFrame with student_id and ability columns
        booklet: Booklet containing items to respond to
        seed: Random seed for reproducibility

    Returns:
        DataFrame with columns: student_id, <item_id_1>, <item_id_2>, ...
        Each item column contains binary scores (0 or 1).
    """
    if "id" not in students.columns or "ability" not in students.columns:
        raise ValueError("students DataFrame must have 'id' and 'ability' columns")

    if booklet.item_count == 0:
        raise ValueError("booklet must contain at least one item")

    abilities = students["ability"].to_numpy()

    items = booklet.get_items_sorted()
    item_ids = [item.column_name for item in items]
    difficulties = np.array([item.logit for item in items])

    n_students = len(abilities)
    n_items = len(difficulties)

    abilities_col = abilities.reshape(-1, 1)  # (n_students,) -> (n_students, 1)
    difficulties_row = difficulties.reshape(1, -1)  # (n_items,) -> (1, n_items)
    # Calculate probability of failure P_fail = 1 / (1 + exp(ability - difficulty))
    probabilities = 1.0 / (1.0 + np.exp(abilities_col - difficulties_row))

    # Derive a deterministic seed from the input parameters using Adler-32 checksum.
    numeric_seed = zlib.adler32(f"{seed}-{n_students}-{n_items}".encode())
    rng = np.random.default_rng(numeric_seed)

    # Generate a random number for each position in students x items.
    random_numbers = rng.uniform(size=(n_students, n_items))

    # Scores: 1 when random number exceeds probability of failure.
    scores = (random_numbers > probabilities).astype(int)

    # Create DataFrame with item IDs as columns.
    scores_df = pl.DataFrame(scores, schema=item_ids)
    # Return widened DF, including original student rows.
    return pl.concat([students, scores_df], how="horizontal")
