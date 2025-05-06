from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import JournalEntry, DailyQuote, SleepRecord, WaterIntakeRecord, FavoriteSong

admin.site.register(DailyQuote)
admin.site.register(JournalEntry)
admin.site.register(SleepRecord)
admin.site.register(WaterIntakeRecord)
admin.site.register(FavoriteSong)