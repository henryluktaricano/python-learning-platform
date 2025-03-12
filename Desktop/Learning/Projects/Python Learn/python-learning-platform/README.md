# Python Interactive Learning Platform

An interactive Python learning platform with AI-assisted feedback and notebook-style code execution.

![Python Learning Platform](https://img.shields.io/badge/Python-Learning%20Platform-blue)

## Features

- **Interactive Code Execution**: Write and run Python code directly in your browser
- **AI-Assisted Evaluation**: Get detailed feedback on your code from OpenAI models
- **Notebook-Style Interface**: Similar to Jupyter notebooks for a familiar experience
- **Structured Exercises**: Organized by chapters and lessons
- **Token Usage Tracking**: Monitor your OpenAI API usage
- **Dark Mode Support**: Choose between light and dark themes
- **Reference Material**: Access markdown-rendered notes for each topic

## Technology Stack

- **Frontend**: Next.js + React + TailwindCSS + ShadcnUI
- **Backend**: FastAPI + Python
- **Database**: SQLite (for token usage and feedback storage)
- **AI**: OpenAI GPT models for code evaluation

## Project Structure

```
python-learning-platform/
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js App Router
│   ├── components/         # React components
│   └── ...
├── backend/                # FastAPI backend
│   ├── app/                # API endpoints and services
│   ├── database/           # Database modules
│   └── ...
├── exercises/              # JSON exercise files
├── notebooks/              # Jupyter notebooks for references
└── database/               # SQLite database files
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- OpenAI API key

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/python-learning-platform.git
   cd python-learning-platform
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

4. Set your OpenAI API key:
   
   **Option 1: Using a .env file (recommended for development)**
   
   Create or edit the `.env` file in the backend directory:
   ```bash
   cd ../backend
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```
   
   **Option 2: Using environment variables**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"  # On Windows: set OPENAI_API_KEY=your-api-key-here
   ```

### Running the Application

Start both the frontend and backend with the provided script:

```bash
./start.sh  # On Windows, you'll need to run the commands separately
```

Or run them individually:

```bash
# Backend
cd backend
source venv/bin/activate
python run_backend.py

# Frontend (in a separate terminal)
cd frontend
npm run dev
```

Then open your browser to:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Adding Exercises

Exercises are stored in JSON format in the `exercises/` directory. The index file (`exercises/index.json`) organizes them by chapter and notebook.

## License

MIT License 