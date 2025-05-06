from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from django.utils import timezone
from .models import JournalEntryTest as JournalEntry, DailyQuote, SleepRecord, WaterIntakeRecord, FavoriteSong


class UserTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="Testpass123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("Testpass123"))


class JournalEntryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="Testpass123"
        )

    def test_create_journal_entry(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            date=date.today(),
            mood="Happy",
            entry="This is a test journal entry"
        )
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.mood, "Happy")
        self.assertEqual(entry.entry, "This is a test journal entry")

    def test_edit_journal_entry(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            date=date.today(),
            mood="Happy",
            entry="Original entry"
        )
        entry.entry = "Updated entry"
        entry.save()
        entry.refresh_from_db()
        self.assertEqual(entry.entry, "Updated entry")

    def test_delete_journal_entry(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            date=date.today(),
            mood="Sad",
            entry="This is a journal entry to be deleted"
        )
        entry_id = entry.id
        entry.delete()
        with self.assertRaises(JournalEntry.DoesNotExist):
            JournalEntry.objects.get(id=entry_id)


class WaterIntakeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="Testpass123"
        )

    def test_increment_water_intake(self):
        record = WaterIntakeRecord.objects.create(
            user=self.user,
            date=date.today(),
            intake_ml=500
        )
        self.assertEqual(record.intake_ml, 500)
        record.intake_ml += 250
        record.save()
        record.refresh_from_db()
        self.assertEqual(record.intake_ml, 750)


class SleepLoggingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="Testpass123"
        )

    def test_log_sleep_duration(self):
        sleep_record = SleepRecord.objects.create(
            user=self.user,
            date=date.today(),
            sleep_time=timezone.make_aware(timezone.datetime(2025, 5, 5, 22, 0)),
            wake_time=timezone.make_aware(timezone.datetime(2025, 5, 6, 6, 0))
        )
        self.assertEqual(sleep_record.user, self.user)
        self.assertEqual(sleep_record.sleep_time.hour, 22)
        self.assertEqual(sleep_record.wake_time.hour, 6)
