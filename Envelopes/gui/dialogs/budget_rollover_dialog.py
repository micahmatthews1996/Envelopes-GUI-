from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QScrollArea, QVBoxLayout, QWidget)

from services.budget_service import BudgetRolloverItem
from utils.money import format_currency


@dataclass(slots=True)
class RolloverChoice:
    item: BudgetRolloverItem
    destination: str
    goal_id: str = ""


class BudgetRolloverDialog(QDialog):
    """Choose a destination for each positive unused budget amount."""

    def __init__(self, source_month, destination_month, items, accounts, goals, parent=None):
        super().__init__(parent)
        self._items = [item for item in items if item.unused_cents > 0]
        self._accounts = accounts
        self._goals = goals
        self._rows = []
        self.setWindowTitle("Roll Over Previous Month")
        self.setMinimumWidth(720)
        layout = QVBoxLayout(self)
        title = QLabel(f"{source_month.strftime('%B %Y')} → {destination_month.strftime('%B %Y')}")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Choose what to do with each positive unused amount. Nothing is changed until you confirm."))

        form = QFormLayout()
        for item in self._items:
            row = QWidget(); row_layout = QHBoxLayout(row); row_layout.setContentsMargins(0,0,0,0)
            amount = QLabel(f"{item.category_name}: {format_currency(item.unused_cents)} unused")
            destination = QComboBox()
            destination.addItem("Roll into next month's budget", "budget")
            destination.addItem("Move to a savings goal", "goal")
            destination.addItem("Move to general savings", "savings")
            destination.addItem("Leave unassigned", "unassigned")
            goal = QComboBox(); goal.setVisible(False)
            for savings_goal in goals:
                goal.addItem(savings_goal.name, savings_goal.goal_id)
            destination.currentIndexChanged.connect(lambda _=0, d=destination, g=goal: g.setVisible(d.currentData() == "goal"))
            row_layout.addWidget(destination, 2); row_layout.addWidget(goal, 2)
            form.addRow(amount, row)
            self._rows.append((item, destination, goal))
        content = QWidget(); content.setLayout(form)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(content); layout.addWidget(scroll)

        source_accounts = [a for a in accounts if a.account_type != "Savings"]
        savings_accounts = [a for a in accounts if a.account_type == "Savings"]
        self.source_account = QComboBox(); self.savings_account = QComboBox()
        for account in source_accounts: self.source_account.addItem(account.name, account.account_id)
        for account in savings_accounts: self.savings_account.addItem(account.name, account.account_id)
        account_form = QFormLayout(); account_form.addRow("Savings transfer from:", self.source_account); account_form.addRow("Savings account:", self.savings_account); layout.addLayout(account_form)
        note = QLabel("The account selections are only used for rows sent to General Savings or a Savings Goal.")
        note.setWordWrap(True); layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Review & Apply")
        buttons.accepted.connect(self._validate); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def _validate(self):
        choices = self.get_choices()
        if any(c.destination == "goal" for c in choices) and not self._goals:
            QMessageBox.warning(self, "No Savings Goals", "Create an active savings goal before choosing a goal destination."); return
        if any(c.destination in {"goal", "savings"} for c in choices):
            if self.source_account.currentData() is None or self.savings_account.currentData() is None:
                QMessageBox.warning(self, "Savings Accounts Required", "Savings rollover requires a source account and a Savings account."); return
        lines=[]
        goal_names={g.goal_id:g.name for g in self._goals}
        for c in choices:
            amount=format_currency(c.item.unused_cents)
            if c.destination=="budget": target=f"{c.item.category_name} next-month budget"
            elif c.destination=="goal": target=f"Savings Goal: {goal_names.get(c.goal_id, 'Unknown')}"
            elif c.destination=="savings": target="General Savings"
            else: target="Leave Unassigned"
            lines.append(f"{c.item.category_name}: {amount} → {target}")
        message = "Apply these rollover choices?\n\n" + "\n".join(lines)
        response=QMessageBox.question(self,"Confirm Budget Rollover",message,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if response==QMessageBox.StandardButton.Yes: self.accept()

    def get_choices(self):
        return [RolloverChoice(item, str(dest.currentData()), str(goal.currentData() or "")) for item,dest,goal in self._rows]

    def get_account_ids(self):
        return str(self.source_account.currentData() or ""), str(self.savings_account.currentData() or "")
