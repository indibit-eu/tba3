"""Student data generation with abilities and covariates."""

import uuid
import zlib

import numpy as np
import polars as pl

from generator.profiles import ClassProfile, CovariateDistribution

_ADJECTIVES = [
    "schnell",
    "langsam",
    "gross",
    "klein",
    "hell",
    "dunkel",
    "leise",
    "laut",
    "warm",
    "kalt",
    "neu",
    "alt",
    "jung",
    "weit",
    "nah",
    "hoch",
    "tief",
    "breit",
    "schmal",
    "rund",
]
_NOUNS = [
    "apfel",
    "birne",
    "kirsche",
    "banane",
    "orange",
    "traube",
    "pflaume",
    "himbeere",
    "erdbeere",
    "zitrone",
    "baum",
    "blume",
    "wolke",
    "stern",
    "mond",
    "sonne",
    "berg",
    "fluss",
    "wald",
    "wiese",
]


def generate_students(
    count: int,
    profile: ClassProfile,
    seed: str,
    covariates: tuple[CovariateDistribution, ...],
) -> pl.DataFrame:
    """Generate a DataFrame of students with abilities and covariates.

    Args:
        count: Number of students to generate
        profile: Class profile defining ability distribution
        covariates: Covariate distributions to apply
        seed: Random seed string for reproducibility (empty for random)

    Returns:
        DataFrame with columns: student_id, name, ability, and covariate columns
    """
    if count < 1:
        raise ValueError("count must be at least 1")

    numeric_seed = zlib.adler32(seed.encode())
    rng = np.random.default_rng(numeric_seed)

    # Generate student IDs (16 bytes = 128 bits per UUID)
    random_bytes = rng.integers(0, 256, size=(count, 16), dtype=np.uint8)
    student_ids = [str(uuid.UUID(bytes=row.tobytes())) for row in random_bytes]

    # Generate student names
    adj_choices = rng.choice(_ADJECTIVES, size=count)
    noun_choices = rng.choice(_NOUNS, size=count)
    numbers = rng.integers(10, 100, size=count)
    names = [
        f"{adj}.{noun}.{number}"
        for adj, noun, number in zip(adj_choices, noun_choices, numbers, strict=True)
    ]

    # Generate abilities from normal distribution
    abilities = rng.normal(
        loc=profile.ability_mean,
        scale=profile.ability_std,
        size=count,
    )

    data: dict[str, list[str] | list[float]] = {
        "id": student_ids,
        "name": names,
        "ability": abilities.tolist(),
    }

    # Add covariates
    for cov in covariates:
        cov_values = rng.choice(
            cov.categories,
            size=count,
            p=cov.probabilities,
        )
        data[cov.type_name] = cov_values.tolist()

    return pl.DataFrame(data)
