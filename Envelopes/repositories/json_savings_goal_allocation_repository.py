import json
from pathlib import Path

from models.savings_goal_allocation import (
    SavingsGoalAllocation,
)


class JsonSavingsGoalAllocationRepository:
    """Stores savings-goal allocations in a JSON file."""

    def __init__(
        self,
        file_path: Path,
    ) -> None:
        self._file_path = file_path

        if not self._file_path.exists():
            self._write_allocations([])

    def get_all(
        self,
    ) -> list[SavingsGoalAllocation]:
        """Return every stored savings-goal allocation."""

        with open(
            self._file_path,
            "r",
            encoding="utf-8",
        ) as file:
            allocation_data = json.load(file)

        return [
            SavingsGoalAllocation.from_dictionary(
                item
            )
            for item in allocation_data
        ]

    def get_by_goal_id(
        self,
        goal_id: str,
    ) -> list[SavingsGoalAllocation]:
        """Return allocations assigned to one goal."""

        return [
            allocation
            for allocation in self.get_all()
            if allocation.goal_id == goal_id
        ]

    def get_by_source(
        self,
        source_type: str,
        source_id: str,
    ) -> list[SavingsGoalAllocation]:
        """Return allocations created by one source."""

        return [
            allocation
            for allocation in self.get_all()
            if (
                allocation.source_type
                == source_type
                and allocation.source_id
                == source_id
            )
        ]

    def add(
        self,
        allocation: SavingsGoalAllocation,
    ) -> None:
        """Persist a new savings-goal allocation."""

        allocations = self.get_all()
        allocations.append(allocation)

        self._write_allocations(
            allocations
        )

    def save_all(
        self,
        allocations: list[
            SavingsGoalAllocation
        ],
    ) -> None:
        """Persist every savings-goal allocation."""

        self._write_allocations(
            allocations
        )

    def delete_by_goal_id(
        self,
        goal_id: str,
    ) -> None:
        """Delete all allocations assigned to one goal."""

        allocations = [
            allocation
            for allocation in self.get_all()
            if allocation.goal_id != goal_id
        ]

        self._write_allocations(
            allocations
        )

    def delete_by_source(
        self,
        source_type: str,
        source_id: str,
    ) -> None:
        """Delete all allocations created by one source."""

        allocations = [
            allocation
            for allocation in self.get_all()
            if not (
                allocation.source_type
                == source_type
                and allocation.source_id
                == source_id
            )
        ]

        self._write_allocations(
            allocations
        )

    def _write_allocations(
        self,
        allocations: list[
            SavingsGoalAllocation
        ],
    ) -> None:
        """Write savings-goal allocations to disk."""

        with open(
            self._file_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                [
                    allocation.to_dictionary()
                    for allocation in allocations
                ],
                file,
                indent=4,
            )