"""Core generator orchestration for class data generation."""

from dataclasses import dataclass

import polars as pl

from generator.booklets import Booklet
from generator.profiles import ClassProfile, CovariateDistribution
from generator.responses import generate_item_responses
from generator.students import generate_students


@dataclass
class GroupData:
    """Complete generated data for a class/group.

    Attributes:
        group_id: Unique identifier for this group
        booklet: The test booklet used
        students: DataFrame with id, name, ability, and covariate columns
        responses: DataFrame with id, name, and one column per item (scores 0/1)
        profile: The class profile used for generation
    """

    group_id: str
    booklet: Booklet
    students: pl.DataFrame
    responses: pl.DataFrame
    profile: ClassProfile

    @property
    def student_ids(self) -> list[str]:
        """Return list of student IDs from the responses DataFrame."""
        return self.responses["id"].to_list()

    @property
    def student_names(self) -> list[str]:
        """Return list of student names from the responses DataFrame."""
        return self.responses["name"].to_list()

    @property
    def covariate_columns(self) -> list[str]:
        """Return covariate column names (all student columns except id/name/ability)."""
        return [c for c in self.students.columns if c not in {"id", "name", "ability"}]


def generate_group(
    group_id: str,
    booklet: Booklet,
    profile: ClassProfile,
    student_count: int,
    covariates: tuple[CovariateDistribution, ...],
    seed: str | None = None,
) -> GroupData:
    """Generate complete class data including students and item responses.

    This is the main entry point for generating test data for a class.

    Args:
        group_id: Unique identifier for the group
        booklet: Test booklet with items
        profile: Class profile
        student_count: Number of students
        covariates: Covariate distributions to use
        seed: Optional seed string. If set, used as the random seed;
            otherwise group_id is used as seed.

    Returns:
        GroupData containing all generated data
    """
    seed_str = seed if seed is not None else group_id

    students = generate_students(
        count=student_count,
        profile=profile,
        covariates=covariates,
        seed=seed_str,
    )

    responses = generate_item_responses(
        students=students,
        booklet=booklet,
        seed=seed_str,
    )

    return GroupData(
        group_id=group_id,
        booklet=booklet,
        students=students,
        responses=responses,
        profile=profile,
    )
