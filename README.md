# 🌟 Aura - AI-Powered Academic Scheduler

Aura is an intelligent scheduling assistant that transforms your academic syllabi into optimized study plans, automatically synced with Google Calendar. Built for students who want to stay organized and maximize their productivity.

![Aura Banner](assets/banner.png)

## ✨ Features

- 📄 **Smart Syllabus Parsing**: Upload PDF or DOCX syllabi and automatically extract assignments, exams, and deadlines
- 🤖 **AI Schedule Generation**: Google Gemini AI creates personalized study plans based on your workload
- 📅 **Google Calendar Integration**: Real-time sync with your Google Calendar
- 📥 **ICS Export**: Download schedules in standard iCalendar format for any calendar app
- 💬 **Natural Language Feedback**: Refine schedules using conversational feedback
- 🎨 **Beautiful UI**: Modern, responsive design with dark theme
- ⚡ **Fast & Reliable**: Built with FastAPI and React for optimal performance

## 🎯 Use Cases

- **Students**: Manage multiple course syllabi and never miss a deadline
- **Educators**: Help students visualize their semester workload
- **Study Groups**: Share and coordinate study schedules
- **Academic Advisors**: Assist students with time management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google Cloud Platform account (for Calendar API)
- Google Generative AI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/aura.git
   cd aura
   ```

2. **Set up Backend**
   ```bash
   cd backend
   python -m venv aura_venv
   
   # Windows
   .\aura_venv\Scripts\Activate.ps1
   
   # macOS/Linux
   source aura_venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   
   Create `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
   ```

4. **Set up Frontend**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Run the Application**
   
   **Terminal 1 - Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
   
   **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Access the Application**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

## 📖 How It Works

### 1. Upload Syllabus
Drag and drop your course syllabus (PDF or DOCX format) into the upload area.

### 2. Extract Events
AI parses the document to extract:
- Course lectures and office hours
- Assignment due dates
- Exam schedules
- Project milestones

### 3. Generate Schedule
Google Gemini AI creates an optimized study plan with:
- Study sessions for each topic
- Revision blocks before exams
- Prep time for assignments
- Balanced workload distribution

### 4. Refine with Feedback
Use natural language to customize:
- "Add more study time for Chapter 3"
- "Schedule morning study sessions"
- "Increase revision time before exams"

### 5. Export & Sync
- **Accept & Export**: Sync directly to Google Calendar
- **Download ICS**: Import into any calendar application

## 🏗️ Architecture

```
┌─────────────────┐
│   React Frontend│
│  (TypeScript)   │
└────────┬────────┘
         │
         │ HTTP/REST API
         │
┌────────▼────────┐
│  FastAPI Backend│
│    (Python)     │
├─────────────────┤
│ Agent 1: Ingest │ ← PDF/DOCX Parsing
│ Agent 2: Verify │ ← Validation
│ Agent 3: Schedule│ ← AI Generation
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼───┐  ┌──▼──────┐
│Gemini │  │ Google  │
│  AI   │  │Calendar │
└───────┘  └─────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 19.2** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS v4** - Styling
- **React Router** - Navigation
- **Axios** - API client

### Backend
- **FastAPI** - Web framework
- **Python 3.8+** - Programming language
- **Google Generative AI** - Schedule generation
- **Google Calendar API** - Calendar integration
- **PyMuPDF** - PDF parsing
- **python-docx** - DOCX parsing
- **Pydantic** - Data validation

## 📚 Documentation

- [Backend README](backend/README.md) - API documentation and setup
- [Frontend README](frontend/README.md) - UI components and development
- [API Documentation](http://localhost:8000/docs) - Interactive API explorer

## 🔐 Security & Privacy

- **Service Account Authentication**: Google Calendar uses secure service account credentials
- **No Data Storage**: Uploaded files are processed in memory, not stored
- **API Key Security**: Environment variables keep keys secure
- **CORS Protection**: Configured for specific frontend origin

## 🐛 Troubleshooting

### Google Calendar Not Syncing
1. Verify service account JSON is correctly set in `.env`
2. Ensure Calendar API is enabled in GCP
3. Check backend logs for error messages

### Syllabus Parsing Issues
- Ensure PDF is text-based (not scanned images)
- Check document structure and formatting
- Try DOCX format as alternative

### Build Errors
```bash
# Clear caches
cd frontend && rm -rf node_modules package-lock.json
cd ../backend && rm -rf __pycache__ aura_venv

# Reinstall
npm install
pip install -r requirements.txt
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Generative AI for powerful schedule generation
- FastAPI community for excellent documentation
- React and Vite teams for modern development tools
- All contributors and testers

## 📧 Contact

- **Project Maintainer**: [Your Name](mailto:your.email@example.com)
- **GitHub Issues**: [Report a bug](https://github.com/yourusername/aura/issues)
- **Discussions**: [Join the conversation](https://github.com/yourusername/aura/discussions)

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Microsoft Outlook integration
- [ ] Collaborative scheduling
- [ ] Smart notifications
- [ ] Study session analytics
- [ ] Export to Notion, Trello, etc.

## ⭐ Show Your Support

If you find Aura helpful, please give it a star on GitHub! It helps others discover the project.

---

**Made with ❤️ for students, by students**
