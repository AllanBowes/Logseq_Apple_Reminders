import os
import re
import subprocess
import logging
import traceback
import appscript
from appscript import app, k
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logseq_reminders_sync.log',
    filemode='w'  # Overwrite log file each time
)


class LogseqReminderSync:
    def __init__(self, logseq_graph_path):
        self.logseq_graph_path = logseq_graph_path
        self.todos = []

    def parse_date_and_time(self, todo_text):
        """
        Parse date and time from Logseq TODO with DEADLINE tag
        """
        print(f"\n--- DEBUGGING TODO PARSING ---")
        print(f"Full TODO text: {todo_text}")

        # Regex to extract date and time from DEADLINE tag
        deadline_pattern = r'DEADLINE:\s*<(\d{4})-(\d{2})-(\d{2})\s*\w{3}\s*(\d{1,2}):(\d{2})>'

        match = re.search(deadline_pattern, todo_text)

        if match:
            try:
                # Extract components with explicit type conversion
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))

                # Create datetime object
                full_datetime = datetime(year, month, day, hour, minute)

                # Extract title
                title_match = re.search(r'TODO\s*(.+?)\s*DEADLINE:', todo_text)
                title = title_match.group(1) if title_match else "Untitled Task"

                print(f"Parsed Datetime: {full_datetime}")
                print(f"Title: {title}")
                print("--- END DEBUGGING ---\n")

                return {
                    'title': title.strip(),
                    'description': todo_text.strip(),
                    'deadline': full_datetime
                }

            except Exception as e:
                print(f"PARSING ERROR: {e}")
                logging.error(f"Date parsing error: {e}")
                return None

        print("NO DEADLINE TAG FOUND!")
        return None

    def find_todos(self):
        """
        Locate all TODOs in Logseq graph pages
        """
        todos = set()

        try:
            for root, dirs, files in os.walk(self.logseq_graph_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Look for TODOs with deadlines
                                todo_matches = re.findall(
                                    r'(TODO.+?DEADLINE:\s*<(\d{4})-(\d{2})-(\d{2})\s*\w{3}\s*(\d{1,2}):(\d{2})>)',
                                    content,
                                    re.DOTALL | re.MULTILINE
                                )

                                print(f"\nFile: {file_path}")
                                print(f"Found {len(todo_matches)} TODOs")

                                for todo_match in todo_matches:
                                    todo_text = todo_match[0]
                                    print(f"\nProcessing TODO: {todo_text}")
                                    parsed_todo = self.parse_date_and_time(todo_text)
                                    if parsed_todo:
                                        todos.add((
                                            parsed_todo['title'],
                                            parsed_todo['deadline']
                                        ))
                        except Exception as e:
                            logging.error(f"Error reading file {file_path}: {traceback.format_exc()}")
        except Exception as e:
            logging.error(f"Error walking directory: {traceback.format_exc()}")

        # Convert set of tuples back to list of dictionaries
        self.todos = [
            {
                'title': todo[0],
                'description': todo[0],
                'deadline': todo[1]
            } for todo in todos
        ]

        logging.info(f"Found {len(self.todos)} TODOs with dates")
        print(f"Found {len(self.todos)} TODOs with dates to sync")
        return self.todos

    def create_reminders(self, new_todos):
        """
        Create new reminders in Apple Reminders for the given TODOs
        """
        for todo in new_todos:
            try:
                # Get the deadline datetime
                deadline = todo['deadline']

                # Check if the reminder already exists
                existing_reminders = self.get_existing_reminders(todo['title'])
                if existing_reminders:
                    print(f"Reminder '{todo['title']}' already exists. Skipping.")
                    continue

                # Create the new reminder
                reminder = app('Reminders').default_list.make(
                    new=k.reminder,
                    with_properties={
                        k.name: todo['title'],
                        k.body: todo['description'],
                        k.remind_me_date: deadline
                    }
                )

                logging.info(f"Successfully created reminder: {todo['title']}")
                print(f"Created reminder: {todo['title']} (Date: {deadline})")

            except Exception as e:
                logging.error(f"Unexpected error creating reminder: {todo['title']}")
                logging.error(f"Traceback: {traceback.format_exc()}")
                print(f"Unexpected error creating reminder: {todo['title']}")
                print(f"Traceback: {traceback.format_exc()}")

    def get_existing_reminders(self, title):
        """
        Check if a reminder with the given title already exists
        """
        try:
            reminders = app('Reminders').default_list.reminders()
            return [r for r in reminders if r.name() == title]
        except Exception as e:
            logging.error(f"Error getting existing reminders: {e}")
            return []

    def sync(self):
        """
        Main synchronization method with comprehensive error handling
        """
        try:
            logging.info("Starting Logseq to Reminders Sync")
            print("Starting Logseq to Reminders Sync")

            # Find TODOs
            self.find_todos()

            # Create reminders
            if self.todos:
                print(f"Creating {len(self.todos)} reminders...")
                self.create_reminders(self.todos)
            else:
                print("No TODOs found to sync.")

        except Exception as e:
            logging.error(f"Sync process failed: {traceback.format_exc()}")
            print(f"Sync process failed: {e}")
        finally:
            logging.info("Sync process completed")
            print("Sync process completed")


def main():
    logseq_graph_path = '/Users/allanbowes/.logseq'
    sync_tool = LogseqReminderSync(logseq_graph_path)
    sync_tool.sync()


if __name__ == "__main__":
    main()
