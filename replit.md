# Zoo Management System

## Overview
A Streamlit-based web application for managing zoo operations with role-based authentication and AI-powered observation processing.

**Current State**: Fully functional and running on Replit
**Last Updated**: October 1, 2025

## Project Architecture

### Frontend
- **Framework**: Streamlit (Python web framework)
- **Port**: 5000
- **Host Configuration**: 0.0.0.0 with CORS disabled for Replit proxy compatibility

### Key Features
1. **Role-Based Authentication**
   - Zoo Keeper: Submit and manage animal observations
   - Doctor: Review observations and add medical comments
   - Admin: Full system access and user management

2. **AI Integration**
   - Google Gemini API for processing text observations
   - Deepgram API for audio transcription (optional)
   - Structured data extraction from natural language

3. **Data Management**
   - JSON-based user authentication
   - File-based observation storage (JSON + TXT)
   - Comment system for observations

### File Structure
```
.
├── app.py                      # Main Streamlit application
├── auth.py                     # Authentication module
├── data_manager.py             # Data storage and retrieval
├── zoo_model.py                # AI model integration (Gemini)
├── components/
│   ├── admin_interface.py      # Admin dashboard
│   ├── doctor_interface.py     # Doctor interface
│   └── zookeeper_interface.py  # Zookeeper interface
├── data/
│   ├── observations/           # Stored observations (JSON & TXT)
│   ├── comments/               # Observation comments
│   └── users.json              # User credentials (hashed)
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── pyproject.toml              # Python dependencies (uv)
└── requirements.txt            # Legacy requirements file

```

## Setup & Configuration

### Dependencies
- **Package Manager**: uv (Python 3.11)
- **Key Libraries**:
  - streamlit, streamlit-webrtc, streamlit-audiorecorder
  - google-generativeai (Gemini API)
  - langchain, langchain-core, langchain-huggingface
  - pydantic, python-dotenv
  - scipy, scikit-learn, transformers

### Environment Variables
Optional API keys can be configured in `.env`:
- `GOOGLE_API_KEY` - For Gemini AI processing
- `DEEPGRAM_API_KEY` - For audio transcription

### Workflow
- **Name**: Server
- **Command**: `streamlit run app.py`
- **Port**: 5000
- **Output**: webview

### Deployment
- **Target**: autoscale (stateless web application)
- **Run Command**: streamlit with explicit server configuration

## Demo Credentials
- **Zoo Keeper**: keeper1 / password123
- **Doctor**: doctor1 / medpass456
- **Admin**: admin1 / adminpass789

## Recent Changes
- October 1, 2025: Initial import and setup for Replit environment
  - Renamed `py projects.toml` to `pyproject.toml`
  - Installed all Python dependencies via uv
  - Configured Streamlit for Replit proxy (CORS disabled)
  - Set up workflow on port 5000
  - Updated .gitignore for Python project
  - Configured deployment settings (autoscale)

## Notes
- The application uses file-based storage (no database required)
- AI features are optional - app works with fallback data if APIs not configured
- PyTorch warning can be ignored - not required for core functionality
