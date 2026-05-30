import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from ..models import GymClass, Equipment, Announcement, GymPhoto, SystemSetting, Attendance, Member
from ..forms import GymClassForm, EquipmentForm, AnnouncementForm, GymPhotoForm, SystemSettingForm
from ..decorators import admin_required

# --- Gym Class Management ---
@admin_required
def gym_class_list(request):
    active_branch_id = request.session.get('active_branch_id')
    classes = GymClass.objects.all().select_related('trainer')
    if active_branch_id:
        classes = classes.filter(branch_id=active_branch_id)
    return render(request, 'gym/admin/class_list.html', {'classes': classes})

@admin_required
def gym_class_create(request):
    active_branch_id = request.session.get('active_branch_id')
    if request.method == 'POST':
        form = GymClassForm(request.POST)
        if form.is_valid():
            gym_class = form.save(commit=False)
            if active_branch_id:
                gym_class.branch_id = active_branch_id
            gym_class.save()
            messages.success(request, "Gym class created successfully.")
            return redirect('admin_class_list')
    else:
        form = GymClassForm()
    return render(request, 'gym/admin/class_form.html', {'form': form, 'title': 'Create Class'})

@admin_required
def gym_class_edit(request, pk):
    gym_class = get_object_or_404(GymClass, pk=pk)
    if request.method == 'POST':
        form = GymClassForm(request.POST, instance=gym_class)
        if form.is_valid():
            form.save()
            messages.success(request, "Gym class updated successfully.")
            return redirect('admin_class_list')
    else:
        form = GymClassForm(instance=gym_class)
    return render(request, 'gym/admin/class_form.html', {'form': form, 'title': 'Edit Class'})

@admin_required
def gym_class_delete(request, pk):
    gym_class = get_object_or_404(GymClass, pk=pk)
    if request.method == 'POST':
        gym_class.delete()
        messages.success(request, "Gym class deleted.")
        return redirect('admin_class_list')
    return render(request, 'gym/admin/class_confirm_delete.html', {'object': gym_class})

# --- Equipment Management ---
@admin_required
def equipment_list(request):
    active_branch_id = request.session.get('active_branch_id')
    equipment = Equipment.objects.all()
    if active_branch_id:
        equipment = equipment.filter(branch_id=active_branch_id)
    return render(request, 'gym/admin/equipment_list.html', {'equipment': equipment})

@admin_required
def equipment_create(request):
    active_branch_id = request.session.get('active_branch_id')
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            if active_branch_id:
                item.branch_id = active_branch_id
            item.save()
            messages.success(request, "Equipment added successfully.")
            return redirect('equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'gym/admin/equipment_form.html', {'form': form, 'title': 'Add Equipment'})

@admin_required
def equipment_edit(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipment updated successfully.")
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=item)
    return render(request, 'gym/admin/equipment_form.html', {'form': form, 'title': 'Edit Equipment'})

@admin_required
def equipment_delete(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Equipment removed.")
        return redirect('equipment_list')
    return render(request, 'gym/admin/equipment_confirm_delete.html', {'object': item})

# --- Announcement Management ---
@admin_required
def announcement_list(request):
    active_branch_id = request.session.get('active_branch_id')
    announcements = Announcement.objects.all()
    if active_branch_id:
        announcements = announcements.filter(branch_id=active_branch_id)
    return render(request, 'gym/admin/announcement_list.html', {'announcements': announcements})

@admin_required
def announcement_create(request):
    active_branch_id = request.session.get('active_branch_id')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            if active_branch_id:
                notice.branch_id = active_branch_id
            notice.save()
            messages.success(request, "Announcement posted.")
            return redirect('admin_announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'gym/admin/announcement_form.html', {'form': form, 'title': 'New Announcement'})

@admin_required
def announcement_edit(request, pk):
    notice = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated.")
            return redirect('admin_announcement_list')
    else:
        form = AnnouncementForm(instance=notice)
    return render(request, 'gym/admin/announcement_form.html', {'form': form, 'title': 'Edit Announcement'})

@admin_required
def announcement_delete(request, pk):
    notice = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        notice.delete()
        messages.success(request, "Announcement deleted.")
        return redirect('admin_announcement_list')
    return render(request, 'gym/admin/announcement_confirm_delete.html', {'object': notice})

# --- Gallery Management ---
@admin_required
def gym_photo_list(request):
    active_branch_id = request.session.get('active_branch_id')
    photos = GymPhoto.objects.all()
    if active_branch_id:
        photos = photos.filter(branch_id=active_branch_id)
        
    if request.method == 'POST':
        form = GymPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            if active_branch_id:
                photo.branch_id = active_branch_id
            photo.save()
            messages.success(request, "Photo added to gallery.")
            return redirect('admin_gallery')
    else:
        form = GymPhotoForm()
    return render(request, 'gym/admin/gallery_list.html', {'photos': photos, 'form': form})

@admin_required
def gym_photo_delete(request, pk):
    photo = get_object_or_404(GymPhoto, pk=pk)
    if request.method == 'POST':
        photo.delete()
        messages.success(request, "Photo removed from gallery.")
        return redirect('admin_gallery')
    return render(request, 'gym/admin/photo_confirm_delete.html', {'object': photo})

# --- System Settings ---
@admin_required
def system_settings_edit(request):
    settings, _ = SystemSetting.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = SystemSettingForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "System settings updated.")
            return redirect('system_settings')
    else:
        form = SystemSettingForm(instance=settings)
    return render(request, 'gym/admin/settings_form.html', {'form': form})

# --- QR Check-in System ---
@admin_required
def qr_scanner(request):
    """View to render the QR check-in scanner."""
    return render(request, "gym/admin/qr_scanner.html")

@admin_required
def qr_checkin_api(request):
    """API endpoint to process scanned tokens."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")
            
            member = Member.objects.get(checkin_token=token)
            
            # Check if already checked in today
            today = timezone.now().date()
            active_branch_id = request.session.get('active_branch_id')
            
            if Attendance.objects.filter(member=member, date=today).exists():
                return JsonResponse({
                    "success": False,
                    "message": f"{member.full_name} is already checked in for today."
                })
            
            # Create attendance record
            Attendance.objects.create(
                member=member, 
                date=today,
                branch_id=active_branch_id or member.branch_id
            )
            
            return JsonResponse({
                "success": True,
                "message": f"Successfully checked in {member.full_name}!",
                "member_name": member.full_name,
                "member_id": member.id
            })
            
        except (json.JSONDecodeError, Member.DoesNotExist):
            return JsonResponse({
                "success": False,
                "message": "Invalid token or member not found."
            })
            
    return JsonResponse({"success": False, "message": "Invalid request method."})
