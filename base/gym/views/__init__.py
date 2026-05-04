# This file makes base/gym/views/ a Python package and re-exports every
# view so that urls.py (which does `from . import views`) works unchanged.

from .auth import LoginForm, RegistrationForm, logout_view, register_view, login_redirect_view
from .public import home_view, class_schedule_view, contact_view
from .portal import portal_dashboard, portal_diet, portal_payments, portal_workout
from .trainers import (
    trainer_list, trainer_create, trainer_detail,
    trainer_edit, trainer_delete, assign_trainer,
)
from .trainer_portal import trainer_portal_dashboard, trainer_portal_members
from .fitness import (
    diet_plan_edit,
    exercise_create,
    exercise_delete,
    measurement_create,
    measurement_delete,
    workout_plan_create,
    workout_plan_delete,
    workout_plan_detail,
)
from .members import (
    MemberForm,
    export_members_csv,
    import_members_csv,
    member_create,
    member_delete,
    member_detail,
    member_edit,
    member_list,
)
from .payments import (
    expense_create,
    expense_delete,
    expense_edit,
    expense_list,
    export_payments_csv,
    payment_delete,
    payment_edit,
    record_payment,
    revenue_report,
)
from .plans import (
    assign_membership,
    membership_delete,
    membership_edit,
    plan_create,
    plan_delete,
    plan_edit,
    plan_list,
)
from .reports import attendance_report, dashboard, mark_present

__all__ = [
    # auth
    "LoginForm", "RegistrationForm", "logout_view", "register_view", "login_redirect_view",
    # portal
    "portal_dashboard", "portal_diet", "portal_payments", "portal_workout",
    # members
    "MemberForm", "member_list", "member_create", "member_edit",
    "member_delete", "member_detail", "export_members_csv", "import_members_csv",
    # plans & memberships
    "plan_list", "plan_create", "plan_edit", "plan_delete",
    "assign_membership", "membership_edit", "membership_delete",
    # payments & expenses
    "record_payment", "payment_edit", "payment_delete",
    "expense_list", "expense_create", "expense_edit", "expense_delete",
    "revenue_report", "export_payments_csv",
    # fitness
    "measurement_create", "measurement_delete", "diet_plan_edit",
    "workout_plan_create", "workout_plan_detail", "workout_plan_delete",
    "exercise_create", "exercise_delete",
    # reports
    "dashboard", "mark_present", "attendance_report",
    # trainers (admin)
    "trainer_list", "trainer_create", "trainer_detail",
    "trainer_edit", "trainer_delete", "assign_trainer",
    # trainer portal
    "trainer_portal_dashboard", "trainer_portal_members",
    # public
    "home_view", "class_schedule_view", "contact_view",
]
