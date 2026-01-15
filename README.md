🏛 Public Grievance Management System

A Django-based web application that allows citizens to register complaints, track their status, and view visual insights on complaint resolution.
The system ensures transparency, accountability, and a modern user experience using a dark-themed glassmorphism UI.

🚀 Features
👤 User Side

🔐 Secure Login & Registration

📝 Register Complaints with category, priority & images (before)

📊 Track Complaint Status (Pending / In Progress / Resolved)

📈 Resolution Insights Dashboard

Status-wise graphs

Category-wise analytics

📄 Professional PDF Report

Official watermark

Before & After images

Admin remarks

Resolution date & time

🌙 Dark Theme UI with glassmorphism & animations

🛠 Admin Side

👁 View all complaints in Django Admin

✏️ Update status, after image, and admin comment

🔒 Users are read-only (admin cannot edit/delete user data)

📋 Professional admin panel structure

🧰 Tech Stack
Layer	Technology
Backend	Django 5.x
Frontend	HTML, CSS, Bootstrap 5
Charts	Chart.js
Database	SQLite
PDF Reports	ReportLab
Version Control	Git & GitHub


public_complaint_management_system/
│
├── grievance_system/        # Project settings
├── complaints/              # Core app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── urls.py
│   └── templates/complaints/
│
├── media/                   # Uploaded images
├── templates/
├── static/
├── db.sqlite3               # (ignored in GitHub)
├── manage.py
└── README.md
