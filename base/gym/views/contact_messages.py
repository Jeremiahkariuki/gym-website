from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from ..models import ContactMessage
from ..decorators import admin_required

@admin_required
def contact_message_list(request):
    """Admin view to see all messages from the contact form."""
    contact_messages = ContactMessage.objects.all().order_by("-created_at")
    return render(request, "gym/admin/contact_list.html", {"contact_messages": contact_messages})

@admin_required
def contact_message_detail(request, pk):
    """Admin view to read a full message."""
    message = get_object_or_404(ContactMessage, pk=pk)
    return render(request, "gym/admin/contact_detail.html", {"contact_message": message})

@admin_required
def contact_message_delete(request, pk):
    """Admin view to delete a contact message."""
    message = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        message.delete()
        messages.success(request, "Contact message deleted.")
        return redirect("contact_message_list")
    return render(request, "gym/admin/contact_confirm_delete.html", {"object": message})
