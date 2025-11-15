import csv
from datetime import datetime
from decimal import Decimal
from io import StringIO
from pathlib import Path

from flask import (Blueprint, current_app, flash, redirect, render_template, request,
                   url_for)
from sqlalchemy import func

from . import db
from .models import Account, Budget, RetirementPlan, Transaction


bp = Blueprint("routes", __name__)


def _get_or_create_account(name, account_type="checking"):
    account = Account.query.filter_by(name=name).first()
    if account is None:
        account = Account(name=name, type=account_type)
        db.session.add(account)
    return account


@bp.route("/")
def dashboard():
    budgets = Budget.query.order_by(Budget.category).all()
    transactions = (
        Transaction.query.order_by(Transaction.posted_at.desc()).limit(10).all()
    )
    totals = (
        db.session.query(Transaction.category, func.sum(Transaction.amount))
        .group_by(Transaction.category)
        .order_by(Transaction.category)
        .all()
    )
    retirement_plan = RetirementPlan.query.first()
    return render_template(
        "dashboard.html",
        budgets=budgets,
        transactions=transactions,
        totals=totals,
        retirement_plan=retirement_plan,
    )


@bp.route("/upload", methods=["POST"])
def upload_statement():
    file = request.files.get("statement")
    account_name = request.form.get("account_name") or "Primary"
    account_type = request.form.get("account_type") or "checking"

    if not file or file.filename == "":
        flash("Please select a CSV statement to upload.", "error")
        return redirect(url_for("routes.dashboard"))

    account = _get_or_create_account(account_name, account_type)

    stream = StringIO(file.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)
    count = 0
    for row in reader:
        try:
            posted_at = datetime.strptime(row.get("date"), "%Y-%m-%d").date()
            amount = Decimal(row.get("amount"))
            description = row.get("description", "").strip() or "Imported transaction"
            category = row.get("category") or None
        except (ValueError, KeyError, TypeError) as exc:
            flash(f"Skipping invalid row: {exc}", "error")
            continue

        transaction = Transaction(
            account=account,
            posted_at=posted_at,
            amount=amount,
            description=description,
            category=category,
        )
        db.session.add(transaction)
        count += 1

    db.session.commit()

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / file.filename
    file.stream.seek(0)
    file.save(destination)

    flash(f"Imported {count} transactions from {file.filename}.", "success")
    return redirect(url_for("routes.dashboard"))


@bp.route("/budget", methods=["POST"])
def create_budget():
    category = request.form.get("category")
    monthly_limit = request.form.get("monthly_limit")
    if not category or not monthly_limit:
        flash("Category and limit are required for budgets.", "error")
        return redirect(url_for("routes.dashboard"))
    budget = Budget.query.filter_by(category=category).first()
    if budget:
        budget.monthly_limit = monthly_limit
    else:
        budget = Budget(category=category, monthly_limit=monthly_limit)
        db.session.add(budget)
    db.session.commit()
    flash(f"Budget for {category} saved.", "success")
    return redirect(url_for("routes.dashboard"))


@bp.route("/retirement", methods=["POST"])
def update_retirement():
    target_amount = request.form.get("target_amount", type=float)
    current_savings = request.form.get("current_savings", type=float)
    monthly_contribution = request.form.get("monthly_contribution", type=float)
    expected_return_rate = request.form.get("expected_return_rate", type=float)

    plan = RetirementPlan.query.first()
    if plan is None:
        plan = RetirementPlan()
        db.session.add(plan)

    plan.target_amount = target_amount or plan.target_amount
    plan.current_savings = current_savings or plan.current_savings
    plan.monthly_contribution = monthly_contribution or plan.monthly_contribution
    if expected_return_rate is not None:
        plan.expected_return_rate = expected_return_rate / 100

    db.session.commit()
    flash("Retirement plan updated.", "success")
    return redirect(url_for("routes.dashboard"))
