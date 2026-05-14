from django.shortcuts import render, redirect, get_object_rule
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from ..models import Branch

def is_admin(user):
    return user.is_authenticated and user.is_staff

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address', 'phone', 'email', 'manager_name', 'logo_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

@user_passes_test(is_admin)
def branch_list(request):
    branches = Branch.objects.all().order_by('-created_at')
    return render(request, "gym/admin/branches/branch_list.html", {"branches": branches})

@user_passes_test(is_admin)
def branch_create(request):
    if request.method == "POST":
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("branch_list")
    else:
        form = BranchForm()
    return render(request, "gym/admin/branches/branch_form.html", {"form": form, "title": "Add New Branch"})

@user_passes_test(is_admin)
def branch_edit(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == "POST":
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            return redirect("branch_list")
    else:
        form = BranchForm(instance=branch)
    return render(request, "gym/admin/branches/branch_form.html", {"form": form, "title": "Edit Branch"})

@user_passes_test(is_admin)
def branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == "POST":
        branch.delete()
        return redirect("branch_list")
    return render(request, "gym/admin/branches/branch_confirm_delete.html", {"branch": branch})

@login_required
def set_active_branch(request, branch_id):
    """Sets the active branch for the current session."""
    branch = get_object_or_404(Branch, id=branch_id)
    request.session['active_branch_id'] = branch.id
    request.session['active_branch_name'] = branch.name
    
    # Redirect back to the previous page or dash
    next_url = request.GET.get('next', 'dashboard')
    return redirect(next_url)
