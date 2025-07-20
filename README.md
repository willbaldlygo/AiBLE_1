# AiBLE_1
Claude Code + ChatGPT o3 July 25

# Able2 PDF Research Assistant

Welcome to Able2! This directory contains the complete Able2 PDF Research Assistant application and launcher scripts.

## 🚀 Quick Start Options

### Option 1: Desktop App (Easiest)
1. **Create the desktop app** (one-time setup):
   ```bash
   ./create_desktop_app.sh
   ```
2. **Launch Able2**: Double-click the `Able2.app` icon on your Desktop
3. Terminal opens automatically and starts both servers
4. Browser opens to the application

### Option 2: Command Line Launcher
```bash
./launch_able2.sh
```
This launcher script:
- Automatically sets up dependencies if needed
- Starts both backend and frontend servers
- Opens the application in your browser
- Handles all the setup for you

### Option 3: Direct Project Launch
```bash
cd able2
./start_able2.sh
```

## 📁 Directory Structure

```
/Users/will/Able_2/
├── able2/                     # Main application directory
│   ├── backend/               # Python FastAPI backend
│   ├── frontend/              # React frontend
│   ├── sources/               # PDF file storage
│   ├── data/                  # Vector database storage
│   ├── start_able2.sh         # Project-level startup script
│   └── README.md              # Detailed project documentation
├── launch_able2.sh            # Main launcher script (run from anywhere)
├── create_desktop_app.sh      # Creates desktop app launcher
└── README.md                  # This file
```

## 🔧 First Time Setup

The launcher will automatically handle setup, but you need to:

1. **Install Python 3.8+** and **Node.js 16+** if not already installed
2. **Get an Anthropic API key** from [console.anthropic.com](https://console.anthropic.com)
3. **Run the launcher** - it will guide you through adding your API key

## 💡 What Able2 Does

- **Upload multiple PDFs** simultaneously with drag-and-drop
- **Ask intelligent questions** about your documents using Claude AI
- **Get precise answers** with source attribution showing relevant sections
- **Persistent storage** - documents survive between sessions
- **Vector search** - semantic similarity matching for relevant content

## 🎯 Usage Tips

- Upload multiple PDFs at once by dragging them to the upload area
- Ask questions like "What are the main findings?" or "Summarize the methodology"
- Each answer includes source cards showing where the information came from
- Documents are automatically processed and ready for questions immediately

## 🌐 Access Points

Once running, access Able2 at:
- **Frontend**: http://localhost:3000 or http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔄 Stopping Able2

Press `Ctrl+C` in the Terminal window to stop both servers.

## 📚 More Information

For detailed technical documentation, configuration options, and development information, see `able2/README.md`.

---

**Built with ❤️ for researchers, academics, and anyone who works with documents**

