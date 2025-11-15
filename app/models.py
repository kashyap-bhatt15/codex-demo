from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, func

from . import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Account(db.Model, TimestampMixin):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    type = db.Column(db.String(50), nullable=False)

    transactions = db.relationship("Transaction", back_populates="account", lazy=True)


class Transaction(db.Model, TimestampMixin):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    posted_at = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(80), nullable=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    account = db.relationship("Account", back_populates="transactions")


class Budget(db.Model, TimestampMixin):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False, unique=True)
    monthly_limit = db.Column(db.Numeric(12, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("monthly_limit >= 0", name="ck_budget_positive"),
    )


class RetirementPlan(db.Model, TimestampMixin):
    __tablename__ = "retirement_plans"

    id = db.Column(db.Integer, primary_key=True)
    target_amount = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("1000000"))
    current_savings = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    monthly_contribution = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0"))
    expected_return_rate = db.Column(db.Float, nullable=False, default=0.05)

    __table_args__ = (
        CheckConstraint("target_amount >= 0", name="ck_retirement_target_positive"),
        CheckConstraint("current_savings >= 0", name="ck_retirement_savings_positive"),
        CheckConstraint(
            "monthly_contribution >= 0", name="ck_retirement_contribution_positive"
        ),
    )

    def months_to_goal(self):
        if self.monthly_contribution == 0:
            return None
        remaining = float(self.target_amount - self.current_savings)
        if remaining <= 0:
            return 0
        monthly_return = (1 + float(self.expected_return_rate)) ** (1 / 12) - 1
        balance = float(self.current_savings)
        months = 0
        while balance < float(self.target_amount) and months < 10_000:
            balance = balance * (1 + monthly_return) + float(self.monthly_contribution)
            months += 1
        return months
