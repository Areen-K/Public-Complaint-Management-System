from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse

from .forms import RegisterForm, ComplaintForm
from .models import Complaint

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import os
from django.utils.timezone import localtime


# ================= HOME (DASHBOARD + GRAPHS) =================
from django.db.models import Count
from django.shortcuts import render
from .models import Complaint

def home(request):
    pending = Complaint.objects.filter(status='Pending').count()
    resolved = Complaint.objects.filter(status='Resolved').count()
    in_progress = Complaint.objects.filter(status='In Progress').count()

    category_stats = (
        Complaint.objects
        .values('category')
        .annotate(total=Count('id'))
    )

    category_labels = [c['category'] for c in category_stats]
    category_values = [c['total'] for c in category_stats]

    return render(request, 'complaints/home.html', {
        'pending': pending,
        'resolved': resolved,
        'in_progress': in_progress,
        'category_labels': category_labels,
        'category_values': category_values,
    })

# ================= REGISTER =================
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'complaints/register.html', {'form': form})


# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'complaints/login.html', {'form': form})


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect('login')

# ================= Detect Priotrity =================
def detect_priority(description):
    description = description.lower()

    high_keywords = ['danger', 'accident', 'fire', 'death', 'injured', 'collapse']
    medium_keywords = ['leak', 'broken', 'blocked', 'overflow', 'damage']

    for word in high_keywords:
        if word in description:
            return 'High'

    for word in medium_keywords:
        if word in description:
            return 'Medium'

    return 'Low'

# ================= FILE COMPLAINT =================
@login_required
def file_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user

            # AUTO ASSIGN PRIORITY
            complaint.priority = detect_priority(complaint.description)
            complaint.save()
            return redirect('my_complaints')
    else:
        form = ComplaintForm()

    return render(request, 'complaints/file_complaint.html', {'form': form})


# ================= TRACK STATUS =================
@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'complaints/my_complaints.html', {'complaints': complaints})

@login_required
def complaint_pdf(request, complaint_id):
    complaint = get_object_or_404(
        Complaint,
        id=complaint_id,
        user=request.user
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="complaint_{complaint_id}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    margin_x = 60
    y = height - 60
    line_gap = 18

    # ================= WATERMARK =================
    p.saveState()
    p.setFont("Helvetica-Bold", 50)
    p.setFillGray(0.9, 0.2)
    p.translate(width / 2, height / 2)
    p.rotate(45)
    p.drawCentredString(0, 0, "Public Grievance Management System")
    p.restoreState()

    # ================= HEADER =================
    p.setFont("Helvetica-Bold", 20)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width / 2, y, "Public Complaint Resolution Report")

    y -= 30
    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(
        width / 2,
        y,
        "Transparent complaints • Visual insights • Faster resolutions"
    )

    y -= 40
    p.line(margin_x, y, width - margin_x, y)

    # ================= COMPLAINT DETAILS =================
    y -= 25
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin_x, y, "Complaint Details")

    y -= 20
    p.setFont("Helvetica", 12)

    details = [
        ("Complaint ID", complaint.id),
        ("User", complaint.user.username),
        ("Category", complaint.category),
        ("Priority", complaint.priority),
        ("Status", complaint.status),
        ("Filed On", complaint.created_at.strftime("%d %B %Y, %I:%M %p")),
    ]

    for label, value in details:
        p.drawString(margin_x, y, f"{label}: {value}")
        y -= line_gap

    # ================= DESCRIPTION =================
    y -= 10
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin_x, y, "Complaint Description")

    y -= 18
    p.setFont("Helvetica", 12)
    text = p.beginText(margin_x, y)
    for line in complaint.description.split("\n"):
        text.textLine(line)
    p.drawText(text)

    y = text.getY() - 25

    # ================= IMAGES =================
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin_x, y, "Before / After Images")

    y -= 15
    p.setFont("Helvetica", 11)
    p.drawString(margin_x, y, "Before Image")
    p.drawString(width / 2 + 10, y, "After Image")

    y -= 10

    img_w = (width - margin_x * 2 - 20) / 2
    img_h = 150

    def draw_image(path, x, y):
        try:
            from PIL import Image
            img = Image.open(path)
            iw, ih = img.size
            ratio = min(img_w / iw, img_h / ih)
            p.drawImage(
                path,
                x,
                y - ih * ratio,
                width=iw * ratio,
                height=ih * ratio,
                preserveAspectRatio=True,
                mask="auto"
            )
            p.rect(x, y - ih * ratio, iw * ratio, ih * ratio)
        except:
            pass

    if complaint.before_image:
        draw_image(complaint.before_image.path, margin_x, y)

    if complaint.after_image:
        draw_image(complaint.after_image.path, width / 2 + 10, y)

    y -= img_h + 30

    # ================= ADMIN REMARK =================
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin_x, y, "Admin Remark")

    y -= 18
    p.setFont("Helvetica", 12)
    p.drawString(margin_x, y, complaint.admin_comment or "—")

    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin_x, y, "Resolved By:")

    y -= 18
    p.setFont("Helvetica", 11)
    p.drawString(margin_x, y, "Officer Name: Mr. Rajesh Kumar (Municipal Officer)")
    y -= 15
    p.drawString(margin_x, y, "Contact: +91 98765 43210")
    y -= 15
    # ---------- RESOLUTION DATE ----------
     
    resolved_time = complaint.created_at  # fallback

    if complaint.status == "Resolved":
      resolved_time = localtime(complaint.created_at)

    p.drawString(
     margin_x,
     y,
     "Resolved On: " + resolved_time.strftime("%d %B %Y, %I:%M %p")
)


    # ================= FOOTER =================
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(
        width / 2,
        40,
        "Public Grievance Management System • Made with ❤️ by Swapnil, Areen & Hussey"
    )

    p.drawRightString(width - margin_x, 40, "Page 1")

    # ================= PAGE 2 : GRAPH =================
    p.showPage()

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 60, "Complaint Status Overview")

    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.shapes import Drawing

    drawing = Drawing(400, 250)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 150
    chart.width = 300

    chart.data = [[
        Complaint.objects.filter(status='Pending').count(),
        Complaint.objects.filter(status='Resolved').count(),
        Complaint.objects.filter(status='In Progress').count()
    ]]

    chart.categoryAxis.categoryNames = ['Pending', 'Resolved', 'In Progress']
    chart.valueAxis.valueMin = 0

    drawing.add(chart)
    drawing.drawOn(p, 100, height - 350)

    p.setFont("Helvetica-Oblique", 9)
    p.drawRightString(width - margin_x, 40, "Page 2")

    p.showPage()
    p.save()

    return response
