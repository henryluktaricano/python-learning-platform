# Python Learning Platform

An interactive web application for learning Python programming through structured chapters and exercises.

## Features

- **Interactive Learning**: Complete Python exercises directly in your browser
- **Structured Curriculum**: Organized chapters and topics covering Python fundamentals
- **Code Execution**: Write and run Python code with immediate feedback
- **Progress Tracking**: Monitor your learning journey

## Tech Stack

### Frontend
- Next.js (React framework)
- TypeScript
- Tailwind CSS

### Backend
- FastAPI (Python framework)
- Uvicorn (ASGI server)
- Python 3.9+

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/python-learning-platform.git
   cd python-learning-platform
   ```

2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```
   cd ../frontend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```
   cd backend
   python run.py
   ```
   The backend will be available at http://localhost:8003/api

2. Start the frontend development server:
   ```
   cd frontend
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

3. Or use the convenience script to start both:
   ```
   ./start.sh
   ```

## Project Structure

```
python-learning-platform/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── chapters.py
│   │   │   ├── exercises.py
│   │   │   ├── execute.py
│   │   │   ├── health.py
│   │   │   └── token_tracking.py
│   │   └── main.py
│   ├── exercises/
│   │   └── [chapter_folders]/
│   │       └── [exercise_files].json
│   └── run.py
└── frontend/
    ├── app/
    │   ├── components/
    │   ├── exercises/
    │   ├── chapters/
    │   ├── about/
    │   ├── styles/
    │   └── page.tsx
    ├── public/
    └── package.json
```

## Version Control

This project uses Git for version control. Here are some guidelines for contributing:

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for feature development
- `feature/[feature-name]` - For new features
- `bugfix/[bug-name]` - For bug fixes
- `hotfix/[hotfix-name]` - For urgent production fixes

### Commit Messages

Follow the conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding or modifying tests
- `chore:` for maintenance tasks

Example: `feat: add dark mode to code editor`

### Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes and test locally
3. Push your branch and create a pull request to `develop`
4. After review and approval, the branch will be merged

## Deployment

Instructions for deploying the application to production:

1. Build the frontend:
   ```
   cd frontend
   npm run build
   ```

2. Deploy the backend:
   ```
   cd backend
   # Your deployment commands here
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 