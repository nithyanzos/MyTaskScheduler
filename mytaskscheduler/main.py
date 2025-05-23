# filepath: /workspaces/MyTaskScheduler/mytaskscheduler/main.py
# Main entry point for the Task Scheduler app
from mytaskscheduler import app

if __name__ == "__main__":
    print("Starting Market Risk Task Manager...")
    print("Access the application at: http://127.0.0.1:5000/")
    app.run(debug=True)
