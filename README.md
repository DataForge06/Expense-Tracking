Looking for the app?Download the latest stable version here: v1.0.0 - Latest APK✨ Key Features🔐 Secure User IsolationPrivate Accounts: Every user logs in with their email, creating a completely isolated data environment.Strict Filtering: The backend ensures that User A can never see or modify User B’s data.☁️ Real-Time Cloud SyncCross-Device Access: Since data is stored in MongoDB Atlas, you can log in on any Android phone and find your data ready.FastAPI Backend: A high-performance Python API hosted on Render handles all your transactions securely.📊 Smart Financial InsightsMoney Flow Analysis: A visual flowchart showing exactly how your money moves from Income to Savings.Expense Prediction: Uses daily averages to predict your month-end balance and warn you if you're overspending.Interactive Charts: Clean visual breakdown of your Income vs. Expenses.🧮 Built-in CalculatorsSIP Calculator: Plan your long-term wealth by calculating the future value of your monthly investments.EMI Calculator: Quickly find out your monthly loan installments.🛠️ Technology StackFrontend: Flutter & Dart (Material 3 UI)Backend: FastAPI (Python)Database: MongoDB Atlas (NoSQL)Deployment: Render (Cloud Hosting)Auth: Email-based persistence via Shared Preferences📸 Screenshots(You can add screenshots here by uploading images to an assets/ folder in your repo)Home ScreenMoney FlowSIP Calculator.

⚙️ Installation for Users
Navigate to the Releases section of this repository.

Download app-release.apk.

Install it on your Android device (Allow "Install from Unknown Sources" if prompted).

Enter your email and start tracking! 💸

👨‍💻 Developer Setup
If you want to run the code locally:

Backend:

Navigate to /backend

Create a .env file with your MONGO_URI.

Run uvicorn main:app --reload

Front-End is private so only backend is public.
