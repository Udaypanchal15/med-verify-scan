reminders = []

def add_reminder(name, dosage, frequency, start_time):
    reminder = {
        "name": name,
        "dosage": dosage,
        "frequency": frequency,
        "start_time": start_time
    }
    reminders.append(reminder)
    return reminder
