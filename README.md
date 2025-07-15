# Logseq to Apple Reminders

This Python script is designed to locate TODOs in Logseq, parse the title, date and time and then create a Reminder in Apple Reminders.

It will only locate open TODOs

Before creating a new Reminder, it will check Apple Reminders to see if the TODO already exists and only create new ones if they are not in Reminders

This requires that the TODO has a DATE and TIME by using /Deadline in Logseq

Python 3.1 or higher required on the Mac running Apple Reminders

The appscript library is needed on the Mac. pip3 install appscript

An Apple Shortcut can be created, using “Run Shell Script” and select the Python 3 Shell.