# Aura Frontend

Modern, responsive React application for AI-powered academic schedule management with Google Calendar integration.

## 🚀 Features

- **Syllabus Upload**: Drag-and-drop interface for PDF/DOCX files
- **AI Schedule Generation**: Interactive schedule creation with Gemini AI
- **Google Calendar Integration**: Real-time calendar display via embedded iframe
- **ICS Export**: Download schedules in standard iCalendar format
- **Multi-Step Wizard**: Guided workflow for schedule creation
- **Feedback System**: Apply custom feedback to refine AI-generated schedules
- **Responsive Design**: Beautiful UI with Tailwind CSS v4
- **Dark Theme**: Optimized for extended study sessions

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

## 🛠️ Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

## 🚀 Running the Application

**Development mode with hot reload:**
```bash
npm run dev
```

**Build for production:**
```bash
npm run build
```

**Preview production build:**
```bash
npm run preview
```

The application will be available at: `http://localhost:5173`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # Application entry point
│   ├── index.css               # Global styles & Tailwind config
│   ├── components/
│   │   ├── AuraCalendar.tsx    # Calendar display component
│   │   ├── CalendarOverview.tsx # Calendar summary view
│   │   ├── Categories.tsx      # Event categorization
│   │   ├── GoogleCalendarEmbed.tsx # Google Calendar iframe
│   │   ├── ICSUploadSection.tsx # ICS file upload
│   │   ├── MainCalendar.tsx    # Main calendar interface
│   │   ├── Navbar.tsx          # Navigation bar
│   │   ├── Prioritize.tsx      # Task prioritization
│   │   ├── Sidebar.tsx         # Application sidebar
│   │   ├── ThemeLayout.tsx     # Layout wrapper
│   │   └── UploadSection.tsx   # Syllabus upload component
│   ├── context/
│   │   └── CalendarContext.tsx # Global calendar state
│   ├── pages/
│   │   └── ScheduleUploadPage.tsx # Multi-step schedule wizard
│   └── services/
│       ├── api.service.ts      # Backend API client
│       └── ics.service.ts      # ICS parsing service
├── assets/                     # Static assets (CSS, JS, images)
├── index.html                  # HTML entry point
├── package.json
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── README.md
```

## 🎨 Tech Stack

- **React 19.2.0** - UI library
- **TypeScript 5.9.3** - Type safety
- **Vite 7.2.2** - Build tool and dev server
- **Tailwind CSS v4.1.17** - Utility-first styling
- **React Router 7.2.0** - Client-side routing
- **Axios 1.13.2** - HTTP client
- **date-fns 4.1.0** - Date manipulation
- **ical.js** - ICS parsing

## 🔌 API Integration

The frontend communicates with the backend API through the `api.service.ts` module:

### Key Services

```typescript
// Upload syllabus
await apiService.uploadSyllabus(file);

// Process syllabus
const events = await apiService.processSyllabus(fileId);

// Generate schedule
const schedule = await apiService.generateSchedule(events);

// Apply feedback
const refined = await apiService.applyFeedback(schedule, feedback);

// Sync to Google Calendar
await apiService.syncToGoogleCalendar({ schedule, fixedSchedule });

// Create ICS file
const icsContent = await apiService.createIcs({ schedule, fixedSchedule });

// Get calendar embed URL
const embedUrl = await apiService.getCalendarEmbedUrl();
```

## 🎯 User Workflow

1. **Upload Syllabus**
   - Drag and drop PDF/DOCX file
   - Automatic parsing and event extraction

2. **Review Extracted Events**
   - View parsed assignments, exams, lectures
   - Edit or remove as needed

3. **Generate Schedule**
   - AI creates optimized study plan
   - View proposed schedule with time blocks

4. **Apply Feedback** (Optional)
   - Provide natural language feedback
   - AI refines schedule based on preferences

5. **Export & Sync**
   - **Accept & Export**: Sync to Google Calendar
   - **Download ICS**: Save as iCalendar file
   - **Apply Feedback**: Refine with more feedback

## 🎨 Styling

### Tailwind CSS v4

The project uses Tailwind CSS v4 with CSS-based configuration:

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  --color-black: #000000;
  --color-white: #ffffff;
  --color-floral: #ffffe8;
  --background-floral: #ffffe8;
}
```

### Custom Styles

Additional styles are in `assets/css/main.css` for:
- Typography
- Layout components
- Animations
- Responsive breakpoints

## 🔧 Configuration

### API Base URL

Update in `src/services/api.service.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### Google Calendar Embed

Automatically fetches from backend. Configure calendar settings in backend service.

## 🐛 Troubleshooting

### CORS Errors
Ensure backend CORS is configured to allow frontend origin:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Tailwind Not Working
1. Verify `postcss.config.js` exists
2. Check `@import "tailwindcss"` in `index.css`
3. Restart dev server

### Calendar Not Loading
1. Check backend is running
2. Verify Google Calendar API is configured
3. Check browser console for iframe errors

### Build Errors
```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📦 Dependencies

### Core
- `react` & `react-dom` - UI framework
- `react-router-dom` - Routing
- `typescript` - Type checking

### Utilities
- `axios` - HTTP requests
- `date-fns` - Date formatting
- `ical.js` - ICS parsing
- `clsx` - Conditional classes

### Development
- `vite` - Build tool
- `tailwindcss` - Styling
- `@vitejs/plugin-react` - React support
- `eslint` - Code linting

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

Outputs optimized static files to `dist/` directory.

### Deploy Options
- **Vercel**: `vercel deploy`
- **Netlify**: Connect to Git repository
- **GitHub Pages**: Deploy `dist/` folder
- **Docker**: Create Nginx container with build output

### Environment Variables
Create `.env.production`:
```env
VITE_API_BASE_URL=https://your-backend-api.com/api/v1
```

## 🧪 Testing

```bash
# Run tests (when configured)
npm test

# Type checking
npm run type-check

# Lint code
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow TypeScript and React best practices
4. Write descriptive commit messages
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Related

- [Backend README](../backend/README.md)
- [Main Project README](../README.md)

## 📸 Screenshots

*(Add screenshots of your application here)*

- Homepage with calendar
- Schedule upload wizard
- Generated schedule view
- Google Calendar integration
