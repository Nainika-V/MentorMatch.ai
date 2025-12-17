# MentorMatch.ai 

MentorMatch.ai is a **smart mentorship platform** that seamlessly connects **mentees** with **mentors**, powered by advanced AI capabilities to automate and enhance the learning journey.

---

## 🚀 Features

### 🔍 AI-Powered Mentor Matching
Matches mentees with the most suitable mentors based on skills, goals, and background using machine learning.

### 💬 Real-Time Chat
Mentees and mentors can chat in real time, enabling fluid communication and continuous learning support.

### 📅 Scheduling Meets
Mentors can schedule sessions directly within the platform. Mentees receive notifications and can join with one click.

### 🧭 Personalized AI-Generated Roadmaps
Generates custom learning paths tailored to each mentee’s goals and skill level using Gemini and Serper.

### ✨ AI Assistant Trigger (`@AI Assistant`)
Mentors can type `@AI Assistant` in chat to:
- Create or update roadmaps based on recent chat history.
- Adjust modules dynamically with real-time feedback.

### 📘 Module-Based AI Assessments
After completing each module in the roadmap, mentees receive AI-generated assessments to track progress and retention.

### 🧠 AI-Powered Mock Interviews
Interviews are scheduled at key milestones (midpoint and end) to simulate real-world scenarios and boost confidence.

### 📝 Interview Feedback for Mentors
AI evaluates mentee performance and generates a feedback report sent privately to mentors.

### 🔔 Notifications
Keeps users informed with real-time alerts for new messages, scheduled sessions, roadmap updates, and milestone completions.

---

## 🛠️ Tech Stack

### 🔧 Frontend
- **Next.js**
- **Tailwind CSS**

### 🗄️ Backend
- **Flask (Python)**

### 🗃️ Database
- **MongoDB**

### 🤖 AI & Integrations
- **Gemini** (Google AI for roadmap generation and chat context)
- **AssemblyAI** (audio transcription and NLP)
- **Serper** (web search-based contextual enrichment)
- **gTTS** (text-to-speech support)

---

## 📈 Value Proposition

- **Automates repetitive mentor tasks**: roadmap creation, assessments, and interviews.
- **Personalized learning paths** for every mentee.
- **Continuous feedback loop** to track growth and learning gaps.
- **Human + AI hybrid mentorship**: blends personal touch with scalable AI tools.

---

## 🧪 Getting Started (For Developers)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/gnanikaomkarini/mentormatch.ai.git
   cd mentormatch.ai
   ```

2. **Set Up Backend with Virtual Environment**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies**
   ```bash
   cd ../frontend
   npm install --legacy-peer-deps
   ```

4. **Set Up Environment Variables**
   - Create a `.env` file in both `backend` and `frontend` directories.
   - Add the following variables (replace with your own keys):
     ```plaintext
     MONGO_URI=your-mongodb-uri
     DB_NAME=your-db-name
     JWT_SECRET_KEY=your-jwt-secret

     FLASK_DEBUG=True
     SECRET_KEY=your-secret-key
     PORT=5000
     FRONTEND_URL=http://localhost:3000

     GOOGLE_API_KEY=your-google-api-key
     ASSEMBLYAI_API_KEY=your-assemblyai-api-key
     SERPER_API_KEY=your-serper-api-key
     ```

5. **Run the Application**
   - Start the frontend:
     ```bash
     cd frontend
     npm run dev
     ```
   - Start the backend (in a new terminal):
     ```bash
     cd backend
     source .venv/bin/activate
     python app.py
     ```
   - Open your browser and navigate to `http://localhost:3000` to access the frontend of the app.
   - The backend runs on `http://localhost:5000` by default.

   **Note**: Make sure you have a valid MongoDB connection string in your `.env` file for the backend to work properly.

---

## 🌟 Acknowledgements

- [Gemini](https://cloud.google.com/gemini) for AI-powered roadmap generation.
- [AssemblyAI](https://www.assembly.ai/) for audio transcription and NLP.
- [Serper](https://serper.dev/) for contextual web search enrichment.
- [MongoDB](https://www.mongodb.com/) for scalable database solutions.
- [gTTS](https://gtts.readthedocs.io/) for text-to-speech capabilities.

Built with ❤️ to make mentorship smarter and more accessible.
