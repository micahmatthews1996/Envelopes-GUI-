import json
from pathlib import Path

from models.savings_goal import SavingsGoal


class JsonSavingsGoalRepository:
    """Stores savings goals in a JSON file."""

    def __init__(
        self,
        file_path: Path,
    ) -> None:
        self._file_path = file_path

        if not self._file_path.exists():
            self._write_goals([])

    def get_goals(
        self,
    ) -> list[SavingsGoal]:
        """Return every stored savings goal."""

        with open(
            self._file_path,
            "r",
            encoding="utf-8",
        ) as file:
            goal_data = json.load(file)

        return [
            SavingsGoal.from_dictionary(item)
            for item in goal_data
        ]

    def save_goals(
        self,
        goals: list[SavingsGoal],
    ) -> None:
        """Persist all savings goals."""

        self._write_goals(goals)

    def _write_goals(
        self,
        goals: list[SavingsGoal],
    ) -> None:
        """Write savings goals to disk."""

        with open(
            self._file_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                [
                    goal.to_dictionary()
                    for goal in goals
                ],
                file,
                indent=4,
            )