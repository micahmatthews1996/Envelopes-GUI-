from datetime import datetime
from uuid import uuid4

from models.savings_goal import SavingsGoal
from repositories.json_savings_goal_repository import (
    JsonSavingsGoalRepository,
)


class SavingsGoalService:
    """Provides business logic for savings goals."""

    def __init__(
        self,
        repository: JsonSavingsGoalRepository,
    ) -> None:
        self._repository = repository

    def get_goals(
        self,
        include_archived: bool = False,
    ) -> list[SavingsGoal]:
        """Return savings goals."""

        goals = self._repository.get_goals()

        if include_archived:
            return goals

        return [
            goal
            for goal in goals
            if not goal.is_archived
        ]

    def create_goal(
        self,
        name: str,
        target_amount_cents: int,
        target_date=None,
    ) -> SavingsGoal:
        """Create and store a new savings goal."""

        now = datetime.now()

        goal = SavingsGoal(
            goal_id=str(uuid4()),
            name=name.strip(),
            target_amount_cents=target_amount_cents,
            current_amount_cents=0,
            target_date=target_date,
            is_archived=False,
            celebration_shown=False,
            created_at=now,
            updated_at=now,
        )

        goals = self._repository.get_goals()
        goals.append(goal)

        self._repository.save_goals(goals)

        return goal

    def save_goal(
        self,
        updated_goal: SavingsGoal,
    ) -> None:
        """Persist changes to an existing goal."""

        goals = self._repository.get_goals()

        for index, goal in enumerate(goals):
            if goal.goal_id == updated_goal.goal_id:
                updated_goal.updated_at = (
                    datetime.now()
                )

                goals[index] = updated_goal
                break

        self._repository.save_goals(goals)

    def archive_goal(
        self,
        goal_id: str,
    ) -> None:
        """Archive a savings goal."""

        goals = self._repository.get_goals()

        for goal in goals:
            if goal.goal_id == goal_id:
                goal.is_archived = True
                goal.updated_at = datetime.now()
                break

        self._repository.save_goals(goals)

    def get_goal(
        self,
        goal_id: str,
    ) -> SavingsGoal | None:
        """Return one savings goal."""

        for goal in self._repository.get_goals():
            if goal.goal_id == goal_id:
                return goal

        return None