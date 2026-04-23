from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import DietPlanForm, ExerciseForm, MeasurementLogForm, WorkoutPlanForm
from ..models import DietPlan, Exercise, MeasurementLog, Member, WorkoutPlan


@login_required
def measurement_create(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = MeasurementLogForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.member = member
            measurement.save()
            messages.success(request, "Measurement recorded successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = MeasurementLogForm()
    return render(request, "gym/measurement_form.html", {"form": form, "member": member})


@login_required
def measurement_delete(request, pk):
    measurement = get_object_or_404(MeasurementLog, pk=pk)
    member = measurement.member
    if request.method == "POST":
        measurement.delete()
        messages.success(request, "Measurement deleted successfully.")
        return redirect("member_detail", member_id=member.id)
    return render(
        request,
        "gym/measurement_confirm_delete.html",
        {"measurement": measurement, "member": member},
    )


@login_required
def diet_plan_edit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    diet_plan, _ = DietPlan.objects.get_or_create(member=member, defaults={"calories": 2000})
    if request.method == "POST":
        form = DietPlanForm(request.POST, instance=diet_plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Diet plan updated successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = DietPlanForm(instance=diet_plan)
    return render(request, "gym/diet_plan_form.html", {"form": form, "member": member})


@login_required
def workout_plan_create(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.member = member
            workout.save()
            messages.success(request, "Workout plan created successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = WorkoutPlanForm()
    return render(request, "gym/workout_plan_form.html", {"form": form, "member": member})


@login_required
def workout_plan_detail(request, pk):
    workout = get_object_or_404(WorkoutPlan, pk=pk)
    member = workout.member
    exercises = workout.exercises.all()

    days_dict = {i: {"name": name, "exercises": []} for i, name in Exercise.DAYS}
    for ex in exercises:
        days_dict[ex.day]["exercises"].append(ex)

    return render(
        request,
        "gym/workout_plan_detail.html",
        {"workout": workout, "member": member, "days_dict": days_dict},
    )


@login_required
def workout_plan_delete(request, pk):
    workout = get_object_or_404(WorkoutPlan, pk=pk)
    member = workout.member
    if request.method == "POST":
        workout.delete()
        messages.success(request, "Workout plan deleted successfully.")
        return redirect("member_detail", member_id=member.id)
    return render(
        request,
        "gym/workout_plan_confirm_delete.html",
        {"workout": workout, "member": member},
    )


@login_required
def exercise_create(request, workout_id):
    workout = get_object_or_404(WorkoutPlan, id=workout_id)
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.workout_plan = workout
            exercise.save()
            messages.success(request, "Exercise added successfully.")
            return redirect("workout_plan_detail", pk=workout.id)
    else:
        form = ExerciseForm(initial={"day": request.GET.get("day", 0)})
    return render(request, "gym/exercise_form.html", {"form": form, "workout": workout})


@login_required
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    workout = exercise.workout_plan
    if request.method == "POST":
        exercise.delete()
        messages.success(request, "Exercise deleted successfully.")
        return redirect("workout_plan_detail", pk=workout.id)
    return render(request, "gym/exercise_confirm_delete.html", {"exercise": exercise})
