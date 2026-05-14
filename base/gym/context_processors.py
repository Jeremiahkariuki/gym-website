from .models import Branch

def branch_context(request):
    """Provides branch information to all templates."""
    active_branch_id = request.session.get('active_branch_id')
    active_branch = None
    if active_branch_id:
        try:
            active_branch = Branch.objects.get(id=active_branch_id)
        except Branch.DoesNotExist:
            pass
            
    return {
        'all_branches': Branch.objects.all(),
        'active_branch': active_branch,
    }
