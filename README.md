Bot-Expense Tracker APK✨:


Key Features🔐:

Secure User IsolationPrivate Accounts: Every user logs in with their email, creating a completely isolated data environment.Strict Filtering: The backend ensures that User A can never see or modify User B’s data.

☁️ Real-Time Cloud SyncCross-Device Access: Since data is stored in MongoDB Atlas, you can log in on any Android phone and find your data ready.FastAPI Backend: A high-performance Python API hosted on Render handles all your transactions securely.

📊 Smart Financial InsightsMoney Flow Analysis: A visual flowchart showing exactly how your money moves from Income to Savings.Expense Prediction: Uses daily averages to predict your month-end balance and warn you if you're overspending.Interactive Charts: Clean visual breakdown of your Income vs. Expenses.

🧮 Built-in CalculatorsSIP Calculator: Plan your long-term wealth by calculating the future value of your monthly investments.EMI Calculator: Quickly find out your monthly loan installments.

🛠️ Technology StackFrontend: Flutter & Dart (Material 3 UI)Backend: FastAPI (Python)Database: MongoDB Atlas (NoSQL)Deployment: Render (Cloud Hosting)Auth: Email-based persistence via Shared Preferences

*--New Major Update release Patchnotes--*
updated:

App got major update in UI, new refined UI and Interface Experience has been increased

Authentication System has been implimented

Dark mode and Light Mode has been added

Universal Engine Migration: The application has been rebuilt into a Universal APK. It now contains native drivers for all mobile architectures (arm64-v8a, armeabi-v7a, and x86_64), ensuring a smooth installation on any Android device (v5.0 to v15).

High-Contrast UI Overhaul: We have completely refined the typography and color palette. All text across Login, Sign-Up, and Dashboard screens is now darker and sharper, providing maximum readability in all lighting conditions.

🚀 New Features:

🚀 Bot Expense v2.2.1 — The Compatibility Update
This release marks a significant milestone in our journey. We have officially rebranded from Expense Tracker AI to Bot Expense, optimized our database logic for high-traffic history management, and expanded hardware support for the latest flagship Android devices.

🏷️ Branding & UI Refresh
New Identity: The application has been officially renamed to Bot Expense.

Visual Overhaul: Updated the application launcher icon and splash screen branding.

Contact Integration: Added a "Contact Us" portal in the 3-dot menu with full Dark Theme support.

Title Consistency: Ensured the "Bot Expense" branding is consistent across the Home Screen and Android Manifest.

🛠️ Backend & Database Improvements
History Management Fix: Resolved a critical 405 Method Not Allowed error by introducing a unique path for history item deletion.

Route Prioritization: Restructured FastAPI routes to prevent path overlapping between active transactions and archived history.

Service Logic: Added delete_history_transaction to the service layer for secure, targeted record removal from the MongoDB history collection.

Security: Implemented forced email normalization (lowercase/trimmed) across all API endpoints to ensure data isolation.

📱 Device Compatibility & Performance
Samsung S-Series Support: Integrated NDK architecture filters to support 64-bit processors found in the Samsung S25 Ultra.

Modern OS Optimization: Fully tested and optimized for HyperOS, OxygenOS, and FuntouchOS.

Universal Build: Shifted to a Fat APK (Universal) build strategy to ensure a single installer works on both high-end flagships and budget devices.

Target SDK Update: Updated SDK requirements to support the latest Android 14 security standards.

📦 Installation Guide, Users Navigate to the Releases section of this repository.

Download the app-release.apk.

Open the file and allow "Install from Unknown Sources" if prompted by your system.

If Google Play Protect flags the app, click "Install Anyway" (Standard procedure for private, high-security APKs).

*This app is curently is testing phase before launching so sign in with google option will only available for selected 100 users. Due to the underdevelopement of the app only create account option is available for all users who will download the app. Installation will be successful after disabeling the play protect settings from playstore*



For those who wants reference of Backend:

Navigate to /backend

Create a .env file with your MONGO_URI.

Run uvicorn main:app --reload

Front-End is private so only backend is public.
you have to create your own apk the backend is only for reference.


I am active 2nd student trying to work on new projects too.
Give me feedbacks on the latest release whosoever sees this repository, provide me feedback so I could work on app and my major project



Give me Feedbacks on my Email: osisop7@gmail.com
