# Market Risk Task Manager

A comprehensive task management application designed specifically for market risk managers to:
- Assign and track tasks for team members
- Manage tasks for reporting managers
- Track personal tasks
- Send email reminders for upcoming tasks

## Features

- **Team Tasks Management**: Assign tasks to your team of 12 members, track progress, and monitor deadlines
- **Manager Tasks**: Delegate tasks to your 2 reporting managers
- **Personal Tasks**: Keep track of your own responsibilities
- **Email Reminders**: Get notified about upcoming and overdue tasks
- **Persistent Storage**: All tasks are stored locally in JSON files
- **Search Functionality**: Quickly find tasks across all categories
- **Modern UI**: Clean, intuitive interface with responsive design

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python -m mytaskscheduler.main
   ```
4. Access the application at `http://127.0.0.1:5000`

## Technical Details

- Built with Flask
- Uses file-based JSON storage for persistence
- Bootstrap for responsive UI
- Email reminder simulation (logs emails instead of sending them)
