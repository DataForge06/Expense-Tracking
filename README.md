Looking for the app?
Download the latest stable version here: v1.1.0 - Latest APK✨:
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

Universal Engine Migration: The application has been rebuilt into a Universal FAT APK. It now contains native drivers for all mobile architectures (arm64-v8a, armeabi-v7a, and x86_64), ensuring a smooth installation on any Android device (v5.0 to v15).

High-Contrast UI Overhaul: We have completely refined the typography and color palette. All text across Login, Sign-Up, and Dashboard screens is now darker and sharper, providing maximum readability in all lighting conditions.

🚀 New Features:

Smart Financial Vault (History): Introducing the History Archive. When you perform a "Monthly Reset," your data is no longer just cleared; it is intelligently migrated into a structured vault where you can review past spending by month and year.

Predictive Savings Analytics: The Home Screen now features a real-time Projection Bar. It analyzes your current spending velocity to predict your estimated balance at the end of the month.

Enhanced Data Isolation: We’ve upgraded our backend security to ensure 100% private data silos. Your financial records are strictly tied to your account and are inaccessible to any other user.

🛠️ Critical Bug Fixes:

Resolved "No Transactions Found" (Reset Bug): Implemented a "Final Boss" query logic that identifies transactions regardless of whether the date was stored as a String or a Date Object.

Fixed "Update Error 405": Fully synchronized the Flutter PUT requests with the backend API. Editing transaction titles, amounts, or categories is now seamless and error-free.

Email Case-Sensitivity Patch: Fixed a bug where varied capitalization in emails during login caused data duplication. All account data is now unified and case-insensitive.

⚙️ Technical Specifications:

Version: 2.1.0 (Stable)

Build Size: ~50 MB (Includes all high-res assets and universal drivers).

Security: Integrated a real-time Password Strength Meter and Firebase-backed email verification.

Backend: Optimized for low-latency performance using asynchronous MongoDB drivers.


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
Give me Feedbacks on my Email: osontakke.46@gmail.com
