# Plagiarism Detection — Frontend

**A Reliable and Efficient Method to Detect Plagiarism via Tokenization**

React frontend for the plagiarism detection platform. Implements the full scope: authentication, file upload (code & documents), plagiarism analysis, internet source detection, visual analytics, and PDF report download.

## User flows

1. **Register → Login** — JWT-based auth (bcrypt password hashing)
2. **Dashboard** — Files checked, average similarity, recent reports
3. **Report** — Upload file(s): **Website Source Detection** (single file) or **Two-File Comparison** (code/document)
4. **Processing** — Preprocessing → Lexical Analysis → Tokenization
5. **Results** — Percentage, Low/Medium/High, website similarity breakdown, methodology chart, similarity score bars
6. **History** — List of past results with View / Delete
7. **Download PDF Report** — From result detail page

## Tech stack

- **React 18** + **Vite**
- **React Router 6**
- **Axios** (API client with JWT interceptors)
- **Recharts** (line chart for methodology)

## Run locally

1. Install dependencies:
   ```bash
   cd plagiarism-frontend
   npm install
   ```

2. Start the backend (from project root):
   ```bash
   cd plagiarism-backend
   # activate venv then
   python app.py
   ```
   Backend should run at `http://127.0.0.1:5000`.

3. Start the frontend:
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:5173`. API calls to `/api/*` are proxied to the Flask backend.

## File support

- **Code:** `.py`, `.java`, `.c`, `.cpp`, `.js`
- **Documents:** `.txt`, `.pdf`, `.docx`
- **Max size:** 10MB per file

## Classification

- **Low:** 0–30%
- **Medium:** 31–70%
- **High:** 71–100%
