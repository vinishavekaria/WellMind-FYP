from datetime import date
from django.contrib.auth.models import User  # Import the User model
from accounts.models import JournalEntry

# Ensure that the user exists, or use an existing user
user = User.objects.first()  # Get the first user, or replace with your specific user instance

# Manually creating test entries from January 1st to March 31st
journal_entries = [
    (date(2025, 1, 1), "Happy", "Sample entry for 2025-01-01 with mood Happy."),
    (date(2025, 1, 2), "Sad", "Sample entry for 2025-01-02 with mood Sad."),
    (date(2025, 1, 3), "Stressed", "Sample entry for 2025-01-03 with mood Stressed."),
    # Add more entries for each day as needed...
    (date(2025, 3, 31), "Calm", "Sample entry for 2025-03-31 with mood Calm."),
]

for entry_date, mood, entry_text in journal_entries:
    journal_entry = JournalEntry(
        user=user,  # Use the defined user object
        date=entry_date,  # Manually set the date
        mood=mood,
        entry=entry_text
    )
    journal_entry.save()
