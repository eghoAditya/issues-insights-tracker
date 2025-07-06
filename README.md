# 🛠️ Issues & Insights Tracker

A mini SaaS-style application for submitting, viewing, and managing product issues. Designed for teams to collect and act on user-submitted bugs and feedback with role-based access.

---

## 🚀 Features

- **User Authentication**
  - Email/password login
  - Google OAuth login
- **Issue Management**
  - Users (REPORTERS) can submit issues with severity and attachments
  - Maintainers can update issue status (e.g., ACTIVE, RESOLVED)
  - Admins can delete any issue
- **Dashboard**
  - Visual insights (bar chart) of issues by severity
- **Role-Based Access Control**
  - REPORTER: Submit and view their own issues
  - MAINTAINER: View all issues and update status (UI coming soon)
  - ADMIN: View and delete all issues (UI coming soon)
- **WebSockets** (Partially implemented): For real-time chart updates

---

## 🧑‍💻 Tech Stack

| Layer        | Technology                  |
|--------------|------------------------------|
| Frontend     | [SvelteKit](https://kit.svelte.dev/) |
| Backend      | [FastAPI](https://fastapi.tiangolo.com/) |
| Auth         | JWT, Google OAuth via Google Cloud |
| Database     | PostgreSQL                   |
| ORM          | SQLAlchemy                   |
| Realtime     | WebSocket (FastAPI)          |
| Deployment   | Docker, Docker Compose       |

---

## 📦 Project Structure

issues-insights-tracker/
├── backend/
│ ├── app/
│ ├── Dockerfile
│ └── ...
├── frontend/
│ ├── src/routes/+page.svelte
│ ├── Dockerfile (optional)
│ └── ...
├── docker-compose.yml
└── README.md

yaml
Copy
Edit

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourname/issues-insights-tracker.git
cd issues-insights-tracker
2. Configure environment variables
Backend

Add Google Client ID to .env or hardcode for test

Frontend

Set VITE_GOOGLE_CLIENT_ID in a .env file in frontend/

3. Start the app using Docker
bash
Copy
Edit
docker-compose up --build
Backend: http://localhost:8000

Frontend: http://localhost:5173

4. Create Users
Run inside backend virtualenv or Python container:

bash
Copy
Edit
# Start Python shell or script
from app.auth import get_password_hash
print(get_password_hash("yourpassword"))
Insert into database using psql or pgAdmin:

sql
Copy
Edit
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@example.com', '<hashed_password>', 'ADMIN');
Repeat for MAINTAINER or REPORTER roles.

⚠️ Known Limitations
✅ Role-based logic is implemented in the backend (Admin can delete, Maintainer can update status)

❌ However, the frontend UI for delete (Admin) and status dropdown (Maintainer) is currently not functioning.

✅ WebSocket connection is active, but chart does not update in real-time yet. Requires final WebSocket patch.

💡 Future Improvements
 Fix UI behavior for Admin delete and Maintainer status update

 Enable WebSocket-based chart refresh

 Add pagination and search to issues

 User profile page and role-based dashboard routing

 Email notifications on issue assignment or update

 File preview or download support

👨‍🔧 Maintainers
Developed by Aditya for DeepLogic AI evaluation.
