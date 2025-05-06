from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import JournalEntryForm, ToDoForm 
from .models import JournalEntry, ToDo, DailyQuote, SleepRecord, WaterIntakeRecord, FavoriteSong
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .templatetags.custom_filters import mood_colors 
from collections import OrderedDict
from collections import defaultdict
from datetime import datetime, timedelta, date
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
from django.shortcuts import render
from .models import JournalEntry
from textblob import TextBlob
import calendar
from django.utils import timezone
import spacy
import nltk
from .forms import CustomUserCreationForm
import calendar
import matplotlib.pyplot as plt

# Signup view
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect('index')  # Redirect to the homepage after signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('welcome')  # Redirect after successful login
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully!")
    return redirect('index')  # Redirect to the homepage after logout

# Index view (Home Page)
def index(request):
    return render(request, 'accounts/index.html')  # Render the homepage (index.html)

def settings_view(request):
    return render(request, 'accounts/settings.html')

moods = ['Happy', 'Inspired', 'Grateful', 'Sad', 'Angry', 'Stressed', 'Neutral', 'Calm', 'Reflective']
# Journal Entry view (for submitting and creating entries)
@login_required
def journal_entry_view(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            journal_entry = form.save(commit=False)
            journal_entry.user = request.user
            journal_entry.save()
            messages.success(request, 'Your journal entry has been submitted!')
            return redirect('journal_entries')  # Redirect to a page showing the user's journal entries
    else:
        form = JournalEntryForm()

    return render(request, 'accounts/journal_entry.html', {'form': form})

# View to list all journal entries of the logged-in user
@login_required
def journal_entries_view(request):
    entries = JournalEntry.objects.filter(user=request.user)

    date_filter    = request.GET.get('date',   '').strip()
    mood_filter    = request.GET.get('mood',   '').strip()
    keyword_filter = request.GET.get('keyword','').strip()
    month_filter   = request.GET.get('month',  '').strip()
    sort_order     = request.GET.get('sort',   'newest').strip()

    # Apply filters
    if date_filter:
        entries = entries.filter(date=date_filter)
    if mood_filter:
        entries = entries.filter(mood=mood_filter)
    if keyword_filter:
        entries = entries.filter(Q(entry__icontains=keyword_filter))

    # Only apply month filter if it’s a valid integer 1–12
    if month_filter.isdigit():
        m = int(month_filter)
        if 1 <= m <= 12:
            entries = entries.filter(date__month=m)

    # Sorting
    if sort_order == 'newest':
        entries = entries.order_by('-date')
    else:
        entries = entries.order_by('date')

    # Pagination
    paginator   = Paginator(entries, 5)
    page_number = request.GET.get('page')
    entries     = paginator.get_page(page_number)

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    return render(request, 'accounts/journal_entries.html', {
        'entries': entries,
        'months':  months,
        'moods': moods,
    })

@csrf_exempt
def update_journal_entry(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id)
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Updating the entry with the new text if present
            entry.entry = data.get('entry', entry.entry)
            entry.save()
            return JsonResponse({'success': True, 'message': 'Entry updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_journal_entry(request, entry_id):
    if request.method == "POST":
        try:
            entry = JournalEntry.objects.get(id=entry_id)
            entry.delete()
            return JsonResponse({"success": True, "message": "Entry deleted successfully"})
        except JournalEntry.DoesNotExist:
            return JsonResponse({"success": False, "message": "Entry not found"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def mood_pixel_chart_view(request):
    user = request.user
    this_year = datetime.now().year
    start_date = datetime(this_year, 1, 1).date() 
    end_date = datetime(this_year, 12, 31).date() 

    # Get all journal entries for the current year
    entries = JournalEntry.objects.filter(user=user, date__range=[start_date, end_date])

    # Default dictionary with all dates mapped to 'No Data'
    mood_data = {start_date + timedelta(days=i): 'No Data' for i in range(365)}

    # Fill in actual mood data from user entries
    for entry in entries:
        entry_date = entry.date.date() if isinstance(entry.date, datetime) else entry.date
        mood_data[entry_date] = entry.mood

    # Sort the mood_data dictionary by date (keys)
    mood_data = OrderedDict(sorted(mood_data.items()))

    # Pass both mood_data and mood_colors to the template
    return render(request, 'accounts/mood_chart.html', {
        'mood_data': mood_data,
        'mood_colors': mood_colors,
        'year': this_year
    })

mood_colors = {
    "Happy": "#4CAF50",      # Green
    "Inspired": "#FF9800",   # Orange
    "Grateful": "#FFC107",   # Yellow
    "Sad": "#2196F3",        # Blue
    "Angry": "#F44336",      # Red
    "Stressed": "#795548",   # Brown
    "Neutral": "#9E9E9E",    # Gray
    "Calm": "#8BC34A",       # Light Green
    "Reflective": "#673AB7", # Purple
    "No Data": "#E0E0E0"     # Light Gray (no entry)
}

def analyze_sentiment(entry_text):
    # Perform sentiment analysis using TextBlob
    blob = TextBlob(entry_text)
    sentiment = blob.sentiment.polarity  # Sentiment polarity: -1 (negative) to 1 (positive)
    return sentiment

def sentiment_line_chart_view(request):
    user = request.user
    this_year = datetime.now().year

    # Get the selected month from the GET parameters, default to None
    selected_month = request.GET.get('month', None)

    # If no month is selected, display for the entire year
    if selected_month:
        selected_month = int(selected_month)  
        start_date = datetime(this_year, selected_month, 1).date()
        # Set end_date to the last day of the selected month
        if selected_month == 12:
            end_date = datetime(this_year, 12, 31).date()
        else:
            end_date = datetime(this_year, selected_month + 1, 1).date() - timedelta(days=1)
    else:
        start_date = datetime(this_year, 1, 1).date()
        end_date = datetime(this_year, 12, 31).date()

    # Get all journal entries for the selected month or entire year
    entries = JournalEntry.objects.filter(user=user, date__range=[start_date, end_date])

    # Initialise dictionaries to store sentiment data
    monthly_sentiment = defaultdict(list)  # For monthly averages
    daily_sentiment = defaultdict(list)    # For daily sentiment of the selected month

    # Populate sentiment data for each entry
    for entry in entries:
        entry_date = entry.date.date() if isinstance(entry.date, datetime) else entry.date
        sentiment = analyze_sentiment(entry.entry)  # Perform sentiment analysis
        
        # For monthly sentiment, group by month
        month = entry_date.month  # Get the month 
        monthly_sentiment[month].append(sentiment)
        
        # For daily sentiment, group by day for the selected month
        if selected_month:
            daily_sentiment[entry_date].append(sentiment)

    # Prepare data for the chart
    if selected_month:
        # For the selected month show daily sentiment
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        dates = []
        sentiments = []
        for date in date_range:
            dates.append(date)
            if daily_sentiment[date]:
                avg_sentiment = sum(daily_sentiment[date]) / len(daily_sentiment[date])
            else:
                avg_sentiment = 0  # No entries sentiment is 0
            sentiments.append(avg_sentiment)
    else:
        # For all months, show monthly average sentiment
        months = []
        avg_sentiment = []
        for month in range(1, 13):
            if monthly_sentiment[month]:  
                avg_sentiment.append(sum(monthly_sentiment[month]) / len(monthly_sentiment[month]))
            else:
                avg_sentiment.append(0)  # No entries for this month, so sentiment is 0
            months.append(datetime(this_year, month, 1))  # Use the 1st day of each month for x-axis

        # Create a line chart for the monthly sentiment
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(months, avg_sentiment, color='b', marker='o', label='Monthly Average Sentiment')

        # Format X-axis to show months 
        ax.xaxis.set_major_locator(mdates.MonthLocator()) 
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylim([-1, 1])  # Customise the Y-axis to range from -1 to 1 (sentiment score)
        ax.set_ylabel('Mood Happiness', fontsize=12)
        ax.set_title('Your Mood Tracker for the Year', fontsize=14)
        ax.legend()
        plt.xticks(rotation=45)

        # Save the plot to a PNG image in memory
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', transparent=True) 
        img_buf.seek(0)
        img_data = base64.b64encode(img_buf.read()).decode('utf-8')

        return render(request, 'accounts/sentiment_line_chart.html', {
            'img_data': img_data,
            'selected_month': selected_month 
        })

    # Create a line chart for daily sentiment (selected month)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, sentiments, color='b', marker='o', label='Daily Sentiment')

    # Format X-axis to show the days of the selected month
    ax.xaxis.set_major_locator(mdates.DayLocator()) 
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))  # Show day of the month on X-axis
    ax.set_xlabel('Day of Month', fontsize=12)
    ax.set_ylim([-1, 1])  # Customise the Y-axis to range from -1 to 1 (sentiment score)
    ax.set_ylabel('Mood Happiness', fontsize=12)
    ax.set_title(f'Your Mood Tracker for {start_date.strftime("%B %Y")}', fontsize=14)
    ax.legend()
    plt.xticks(rotation=45)


    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', transparent=True)
    img_buf.seek(0)
    img_data = base64.b64encode(img_buf.read()).decode('utf-8')

    # Return the image data to be rendered in the template
    return render(request, 'accounts/sentiment_line_chart.html', {
        'img_data': img_data,
        'selected_month': selected_month  # Pass the selected month to the template
    })


def generate_mood_pie_chart(mood_count):
    """Generate a pie chart for mood distribution."""
    total_entries = sum(mood_count.values())  # Calculate the total number of mood entries

    # Prepare data for the pie chart
    labels = []
    sizes = []
    colors = []
    for mood, count in mood_count.items():
        if count > 0:
            labels.append(f"{mood} ({(count / total_entries) * 100:.1f}%)")
            sizes.append(count)
            colors.append(mood_colors.get(mood, "#E0E0E0"))  # Default color if no entry

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')  


    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True) 
    buf.seek(0)

    pie_chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return pie_chart_base64

def mood_pie_chart_view(request):
    """View to display the mood pie chart with a month filter."""
    user = request.user
    this_year = datetime.now().year

    selected_month = request.GET.get('month', None)

    # Set the start and end date based on selected month
    if selected_month:
        selected_month = int(selected_month)
        start_date = datetime(this_year, selected_month, 1).date()
        if selected_month == 12:
            end_date = datetime(this_year, 12, 31).date()
        else:
            end_date = datetime(this_year, selected_month + 1, 1).date() - timedelta(days=1)
    else:
        start_date = datetime(this_year, 1, 1).date()
        end_date = datetime(this_year, 12, 31).date()

    # Get journal entries for the selected date range
    entries = JournalEntry.objects.filter(user=user, date__range=[start_date, end_date])

    # Initialise dictionary to count moods
    mood_count = defaultdict(int)

    # Classify moods and count them
    for entry in entries:
        mood_count[entry.mood] += 1

    # Check if there are no entries for the selected month
    no_entries_for_month = not entries.exists()

    # Generate the pie chart
    pie_chart_base64 = generate_mood_pie_chart(mood_count) if entries.exists() else None


    # Get the list of months for filtering
    months = [datetime(this_year, month, 1).strftime('%B') for month in range(1, 13)]

    return render(request, 'accounts/mood_pie_chart.html', {
        'pie_chart_base64': pie_chart_base64,
        'selected_month': selected_month,
        'months': months,
        'no_entries_for_month': no_entries_for_month
    })

@login_required
def todo_list(request):
    todos = ToDo.objects.filter(user=request.user)  # Retrieve users todos
    form = ToDoForm()  # Empty form for adding new todo
    
    if request.method == 'POST':  
        form = ToDoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user  
            todo.save()
            return redirect('todo_list')  # Redirect to the same page after saving the todo

    return render(request, 'accounts/todo_list.html', {'form': form, 'todos': todos}) 

@login_required
def delete_todo(request, pk):
    todo = get_object_or_404(ToDo, pk=pk, user=request.user)  # Get the todo for the current user
    todo.delete()  # Delete the todo
    return redirect('todo_list')  # Redirect to the todo list after deletion

@login_required
def amend_todo(request, pk):
    todo = get_object_or_404(ToDo, pk=pk, user=request.user)  # Get the todo to amend for the current user
    if request.method == 'POST':  
        form = ToDoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()  
            return redirect('todo_list')  
    else:
        form = ToDoForm(instance=todo)  
    
    return render(request, 'accounts/amend_todo.html', {'form': form}) 

@login_required
def welcome_page(request):
    user = request.user
    today = timezone.localdate() 
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    # Get weekly todos for the user
    weekly_todos = ToDo.objects.filter(user=user, date_due__range=(start_week, end_week))

    # Get today's journal entry, if any
    try:
        todays_entry = JournalEntry.objects.get(user=user, date=today)
    except JournalEntry.DoesNotExist:
        todays_entry = None

    # Get today's quote
    try:
        quote = DailyQuote.objects.get(date=today)
    except DailyQuote.DoesNotExist:
        quote = "Stay positive, work hard, make it happen."

    # Get today's sleep record, if any
    sleep_record = SleepRecord.objects.filter(user=user, date=today).first()
    water_record, _ = WaterIntakeRecord.objects.get_or_create(user=user, date=today, defaults={'intake_ml': 0})

    sleep_duration = None

    # Track points and streak
    points = 0
    streak = count_consecutive_streak(user)

    # Add points for journal entry if present
    if todays_entry:
        points += 5

    # Add points for water intake if there is any
    if water_record.intake_ml > 0:
        points += 2

    # Add points for sleep record if present
    if sleep_record:
        points += 2

    if request.method == "POST":
        if 'sleep' in request.POST:
            sleep_time_str = request.POST.get('sleep_time')
            wake_time_str = request.POST.get('wake_time')

            if len(sleep_time_str.split(':')) == 2:
                sleep_time_str += ':00'  
            if len(wake_time_str.split(':')) == 2:
                wake_time_str += ':00' 

            SleepRecord.objects.update_or_create(
                user=user, date=today,
                defaults={'sleep_time': sleep_time_str, 'wake_time': wake_time_str}
            )

            sleep_dt = datetime.strptime(sleep_time_str, '%H:%M:%S')
            wake_dt = datetime.strptime(wake_time_str, '%H:%M:%S')
            if wake_dt < sleep_dt:
                wake_dt += timedelta(days=1)

            # Calculate sleep duration
            duration = wake_dt - sleep_dt
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = remainder // 60
            sleep_duration = f"{hours} hours and {minutes} minutes"

        elif 'water' in request.POST:
            water_amount = int(request.POST.get('water_amount'))
            total_intake = int(request.POST.get('total_intake'))

            water_record.intake_ml = total_intake
            water_record.save()

            return redirect('welcome')

    if sleep_record and sleep_record.sleep_time and sleep_record.wake_time:
        sleep_time_str = str(sleep_record.sleep_time)
        wake_time_str = str(sleep_record.wake_time)

        if len(sleep_time_str.split(':')) == 2:
            sleep_time_str += ':00'
        if len(wake_time_str.split(':')) == 2:
            wake_time_str += ':00'

        sleep_dt = datetime.strptime(sleep_time_str, '%H:%M:%S')
        wake_dt = datetime.strptime(wake_time_str, '%H:%M:%S')
        if wake_dt < sleep_dt:
            wake_dt += timedelta(days=1)

        # Calculate sleep duration
        duration = wake_dt - sleep_dt
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60
        sleep_duration = f"{hours} hours and {minutes} minutes"

    # Calculate water intake percentage (2000ml is the goal)
    water_percentage = (water_record.intake_ml / 2000) * 100 if water_record.intake_ml else 0

    return render(request, 'accounts/welcome.html', {
        'username': user.username,
        'weekly_todos': weekly_todos,
        'todays_entry': todays_entry,
        'quote': quote,
        'sleep_record': sleep_record,
        'water_record': water_record,
        'sleep_duration': sleep_duration,
        'water_percentage': water_percentage,
        'points': points,
        'streak': streak
    })

def count_consecutive_streak(user):
    today = timezone.now().date()
    streak = 0
    current_day = today

    while True:
        try:
            # Check if user logged a journal entry on current_day
            JournalEntry.objects.get(user=user, date=current_day)
            streak += 1
        except JournalEntry.DoesNotExist:
            break

        current_day -= timedelta(days=1)  # Check the previous day

    return streak


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nlp = spacy.load("en_core_web_md")

# --- Keyword extraction function ---
def extract_keywords(entry_text):
    """Simple keyword extraction using noun phrases"""
    blob = TextBlob(entry_text)
    try:
        keywords = set(blob.noun_phrases)
    except Exception:
        keywords = set(word.lower() for word in blob.words)
    return keywords

# --- Function to find synonyms using spaCy ---
def find_synonyms(word, keyword_set):
    word_str = str(word)  
    word_doc = nlp(word_str)

    if word_doc.has_vector:
        synonyms = []
        for keyword in keyword_set:
            keyword_str = str(keyword)  
            keyword_doc = nlp(keyword_str)

            if keyword_doc.has_vector:
                similarity = word_doc.similarity(keyword_doc)
                if similarity > 0.7:  
                    synonyms.append(keyword)
        return synonyms
    else:
        return []


# --- Generates personalised tips ---
def get_personalized_tips(entry_text, mood, sleep_hours, water_pct):
    tips = []
    text = (entry_text or "").lower()

    sentiment = analyze_sentiment(text)
    keywords = extract_keywords(text)

    mood_lower = mood.lower()

    # Define mood-specific advice
    if mood_lower == "happy":
        tips.append("Your positivity is contagious—consider sharing a kind word or smile with someone today.")
    elif mood_lower == "inspired":
        tips.append("Capture your inspiration in a sketch, journal entry, or quick brainstorm session.")
    elif mood_lower == "grateful":
        tips.append("Write down three things you’re grateful for—this can reinforce that feeling.")
    elif mood_lower == "sad":
        tips.append("Try a grounding technique like the 5-4-3-2-1 exercise to reconnect with your surroundings.")
        tips.append("Take 5 minutes to do deep belly breathing or listen to calming music.")
    elif mood_lower == "stressed":
        tips.append("Try a short meditation or progressive muscle relaxation.")
        tips.append("Go for a 10-minute walk to clear your mind and release physical tension.")
    elif mood_lower == "angry":
        tips.append("It’s okay to feel angry—try channeling that energy into a productive activity or physical exercise.")
        tips.append("Use a journal to write out what’s bothering you—sometimes clarity helps reduce anger.")
        tips.append("Practice box breathing (inhale 4s, hold 4s, exhale 4s, hold 4s) to calm your body.")
    elif mood_lower == "neutral":
        tips.append("Spend a moment noticing how you feel right now and honor that emotion.")
    else:
        tips.append("Spend some time reflecting on your current mood and how you can nurture your mental well-being.")

    # add supportive tips
    if sentiment < 0:
        tips.append("It seems like you're feeling down. Consider writing down a few positive things or talking to a friend.")

    # Use synonyms
    emotional_keywords = ["cry", "stress", "sad"]

    for word in emotional_keywords:
        synonyms = find_synonyms(word, keywords)
        for synonym in synonyms:
            if synonym == "cry":
                tips.append("It’s okay to express your feelings—crying can help you release emotions.")
            elif synonym == "stress":
                tips.append("Take a break and try mindfulness or deep-breathing exercises to relax.")
            elif synonym == "sad":
                tips.append("Sometimes a walk outside or talking to someone can make you feel better.")

    # 4) Sleep advice
    if sleep_hours < 7:
        tips.append("Aim for 7–8 hours of sleep tonight—try a wind‑down routine like reading or gentle stretches.")
    else:
        tips.append("Great job on your sleep—keep your bedtime routine consistent for lasting benefits.")

    # 5) Hydration advice
    if water_pct < 50:
        tips.append("You’ve had only half your water goal—try filling a reusable bottle and sipping regularly.")
    else:
        tips.append("Nice work staying hydrated—continue to carry your water bottle with you today.")

    return tips

def wellness_tips_view(request):
    user = request.user
    entry_text = None
    mood = None

    # Check if there's a journal entry for today
    today = date.today()
    try:
        journal_entry_today = JournalEntry.objects.get(user=user, date=today)
        entry_text = journal_entry_today.entry
        mood = journal_entry_today.mood
    except JournalEntry.DoesNotExist:
        # Try to fetch the most recent past journal entry
        recent_entry = JournalEntry.objects.filter(user=user).exclude(date=today).order_by('-date').first()
        if recent_entry:
            mood = recent_entry.mood
            entry_text = None  # No text for today
            tips = [
                "No journal entry for today. Based on your last mood entry, here’s something to consider:",
                f"Yesterday you felt {mood.lower()}. Take a moment today to reflect or unwind depending on how you're feeling now."
            ]
        else:
            mood = "Neutral"
            entry_text = None
            tips = ["No journal entry found. Add one to receive personalized wellness tips!"]

    # Retrieve today's sleep and water intake
    try:
        sleep_record = SleepRecord.objects.get(user=user, date=today)
        sleep_hours = (sleep_record.wake_time.hour - sleep_record.sleep_time.hour) % 24
    except SleepRecord.DoesNotExist:
        sleep_hours = 0

    try:
        water_record = WaterIntakeRecord.objects.get(user=user, date=today)
        water_pct = (water_record.intake_ml / 2000) * 100
    except WaterIntakeRecord.DoesNotExist:
        water_pct = 0

    if entry_text:
        tips = get_personalized_tips(entry_text, mood, sleep_hours, water_pct)
    else:
        if sleep_hours < 7:
            tips.append("Try to get more rest tonight—7–8 hours can make a big difference.")
        if water_pct < 50:
            tips.append("You’ve had only part of your water goal—keep sipping regularly today!")

    return render(request, 'accounts/wellness_tips.html', {
        'mood': mood,
        'wellness_tips': tips
    })


# Example playlist 
MOOD_PLAYLISTS = {
    'sleep': [
    'https://www.youtube.com/embed/videoseries?list=PLQ_PIlf6OzqIeHoW1qn9xw3OCaPDvGeF-',
    ],

    'anxiety': [
        'https://www.youtube.com/embed/cbhyB8cpGdg',
    ],
    'stress': [
        'https://www.youtube.com/embed/hsGOT_0L16U?list=PLJvf6TCJJj9afCFbCqu7Kfvsdrie9Apb_',
    ],
    'self-care': [
        'https://www.youtube.com/embed/rnnfFDBokss?list=PLgJ7R6YomsFMtoRhR5L8HlmIHGYCbxZKh',
    ],
    'focus': [
        'https://www.youtube.com/embed/p2_zDvtPQ-g?list=PLerTk5MKpsqsylFgNLJQjZJnttAepRUJ3',
    ],
    'happy': [
        'https://www.youtube.com/embed/ekr2nIex040?list=PLgzTt0k8mXzF2fleyxQ17JxeccHFC8Gxp',
    ],
    'soundscapes': [
        'https://www.youtube.com/embed/kC5k--wqNYk?list=PL1F7117E03613D657',
    ],
    'relaxation': [
        'https://www.youtube.com/embed/lCOF9LN_Zxs?list=PLQ_PIlf6OzqIEvjMOCAZsD21T6xn9QUP6',
    ],
}

def mood_music(request):
    latest_entry = request.user.journalentry_set.last()
    if latest_entry:
        mood = latest_entry.mood.lower()  
    else:
        mood = None

    # Define
    mood_to_playlist = {
        'happy': 'happy',
        'inspired': 'focus',
        'neutral': 'happy',
        'grateful': 'happy',
        'stressed': 'stress',
        'angry': 'relaxation',
        'calm': 'relaxation',
        'reflective': 'relaxation',
        'sad': 'self-care',
    }

    # Get the recommended playlist based on the user's mood
    recommended_playlist_key = mood_to_playlist.get(mood)
    recommended_playlist = MOOD_PLAYLISTS.get(recommended_playlist_key, []) if recommended_playlist_key else []

    all_playlists = MOOD_PLAYLISTS.items()  

    # Get the user's favorited playlists 
    favorite_playlists = FavoriteSong.objects.filter(user=request.user)
    favorite_uris = [favorite.song_uri for favorite in favorite_playlists] 

    return render(request, 'accounts/mood_music.html', {
        'recommended_playlist': recommended_playlist,
        'all_playlists': all_playlists,
        'favorite_uris': favorite_uris,  
        'user_mood': mood,
    })


@login_required
def save_favorite(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            song_url = data.get('song_url')
            
            if song_url:
                favorite_song = FavoriteSong.objects.filter(user=request.user, song_uri=song_url).first()
                
                if favorite_song:
                    # unlike
                    favorite_song.delete()
                    return JsonResponse({'success': True, 'action': 'removed'})
                else:
                    # like
                    FavoriteSong.objects.create(user=request.user, song_uri=song_url)
                    return JsonResponse({'success': True, 'action': 'added'})
            
            return JsonResponse({'success': False, 'error': 'Song URL is missing'})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def mood_dashboard_view(request):
    """
    Combined view for mood pixel chart, sentiment line chart, mood pie chart,
    sleep record bar chart, and water intake bar chart
    """
    user = request.user
    this_year = datetime.now().year
    
    selected_month = request.GET.get('month', None)
    
    if selected_month:
        selected_month = int(selected_month)
        start_date = datetime(this_year, selected_month, 1).date()
        if selected_month == 12:
            end_date = datetime(this_year, 12, 31).date()
        else:
            end_date = datetime(this_year, selected_month + 1, 1).date() - timedelta(days=1)
    else:
        start_date = datetime(this_year, 1, 1).date()
        end_date = datetime(this_year, 12, 31).date()

    entries = JournalEntry.objects.filter(user=user, date__range=[start_date, end_date])
    
    #
    # MOOD PIXEL CHART DATA
    #

    current_date = start_date
    mood_data = {}
    while current_date <= end_date:
        mood_data[current_date] = 'No Data'
        current_date += timedelta(days=1)
    
    for entry in entries:
        entry_date = entry.date.date() if isinstance(entry.date, datetime) else entry.date
        mood_data[entry_date] = entry.mood

    mood_data = OrderedDict(sorted(mood_data.items()))
    
    #
    # MOOD PIE CHART DATA
    #
    
    mood_count = defaultdict(int)

    for entry in entries:
        mood_count[entry.mood] += 1

    pie_chart_base64 = generate_mood_pie_chart(mood_count) if entries.exists() else None
    
    #
    # SENTIMENT LINE CHART DATA
    #
    
    if selected_month:
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        daily_sentiment = defaultdict(list)
        
        for entry in entries:
            entry_date = entry.date.date() if isinstance(entry.date, datetime) else entry.date
            sentiment = analyze_sentiment(entry.entry)
            daily_sentiment[entry_date].append(sentiment)
            
        dates = []
        sentiments = []
        for date in date_range:
            dates.append(date)
            if daily_sentiment[date]:
                avg_sentiment = sum(daily_sentiment[date]) / len(daily_sentiment[date])
            else:
                avg_sentiment = 0
            sentiments.append(avg_sentiment)
            
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, sentiments, color='b', marker='o', label='Daily Sentiment')
        
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax.set_xlabel('Day of Month', fontsize=12)
        ax.set_ylim([-1, 1])
        ax.set_ylabel('Mood Happiness', fontsize=12)
        ax.set_title(f'Your Mood Tracker for {start_date.strftime("%B %Y")}', fontsize=14)
        ax.legend()
        plt.xticks(rotation=45)
    else:
        monthly_sentiment = defaultdict(list)
        
        for entry in entries:
            entry_date = entry.date.date() if isinstance(entry.date, datetime) else entry.date
            sentiment = analyze_sentiment(entry.entry)
            month = entry_date.month
            monthly_sentiment[month].append(sentiment)
            
        months = []
        avg_sentiment = []
        for month in range(1, 13):
            if monthly_sentiment[month]:
                avg_sentiment.append(sum(monthly_sentiment[month]) / len(monthly_sentiment[month]))
            else:
                avg_sentiment.append(0)
            months.append(datetime(this_year, month, 1))
            
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(months, avg_sentiment, color='b', marker='o', label='Monthly Average Sentiment')
        
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylim([-1, 1])
        ax.set_ylabel('Mood Happiness', fontsize=12)
        ax.set_title('Your Mood Tracker for the Year', fontsize=14)
        ax.legend()
        plt.xticks(rotation=45)
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', transparent=True)
    img_buf.seek(0)
    sentiment_chart_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close() 
    
    #
    # SLEEP RECORD BAR CHART DATA
    #
    
    sleep_chart_base64 = None
    
    sleep_records = SleepRecord.objects.filter(user=user, date__range=[start_date, end_date])
    
    if sleep_records.exists():
        if selected_month:
            sleep_data = {}
            date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
            
            for date in date_range:
                sleep_data[date] = 0  
            
            for record in sleep_records:
                if record.sleep_time and record.wake_time:
                    sleep_time_str = str(record.sleep_time)
                    wake_time_str = str(record.wake_time)
                    
                    if len(sleep_time_str.split(':')) == 2:
                        sleep_time_str += ':00'
                    if len(wake_time_str.split(':')) == 2:
                        wake_time_str += ':00'
                    
                    sleep_dt = datetime.strptime(sleep_time_str, '%H:%M:%S')
                    wake_dt = datetime.strptime(wake_time_str, '%H:%M:%S')
                    if wake_dt < sleep_dt:
                        wake_dt += timedelta(days=1)
                    
                    duration = wake_dt - sleep_dt
                    hours = duration.seconds / 3600
                    record_date = record.date.date() if isinstance(record.date, datetime) else record.date
                    sleep_data[record_date] = hours
            
            dates = list(sleep_data.keys())
            hours = list(sleep_data.values())
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(dates, hours, color='#8e44ad', alpha=0.7)
            
            # Add horizontal lines
            ax.axhline(y=7, color='green', linestyle='--', alpha=0.7, label='Ideal Sleep (Min)')
            ax.axhline(y=9, color='red', linestyle='--', alpha=0.7, label='Ideal Sleep (Max)')
            
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
            ax.set_xlabel('Day of Month', fontsize=12)
            ax.set_ylabel('Sleep Duration (Hours)', fontsize=12)
            ax.set_title(f'Your Sleep Pattern for {start_date.strftime("%B %Y")}', fontsize=14)
            ax.legend()
            plt.xticks(rotation=45)
        else:
            monthly_sleep = defaultdict(list)
            
            for record in sleep_records:
                if record.sleep_time and record.wake_time:
                    sleep_time_str = str(record.sleep_time)
                    wake_time_str = str(record.wake_time)
                    
                    if len(sleep_time_str.split(':')) == 2:
                        sleep_time_str += ':00'
                    if len(wake_time_str.split(':')) == 2:
                        wake_time_str += ':00'
                    
                    sleep_dt = datetime.strptime(sleep_time_str, '%H:%M:%S')
                    wake_dt = datetime.strptime(wake_time_str, '%H:%M:%S')
                    if wake_dt < sleep_dt:
                        wake_dt += timedelta(days=1)
                    
                    duration = wake_dt - sleep_dt
                    hours = duration.seconds / 3600
                    record_date = record.date.date() if isinstance(record.date, datetime) else record.date
                    monthly_sleep[record_date.month].append(hours)
            
            months = []
            avg_sleep = []
            for month in range(1, 13):
                if monthly_sleep[month]:
                    avg_sleep.append(sum(monthly_sleep[month]) / len(monthly_sleep[month]))
                else:
                    avg_sleep.append(0)
                months.append(datetime(this_year, month, 1))
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar([month.strftime('%b') for month in months], avg_sleep, color='#8e44ad', alpha=0.7)
            
            ax.axhline(y=7, color='green', linestyle='--', alpha=0.7, label='Ideal Sleep (Min)')
            ax.axhline(y=9, color='red', linestyle='--', alpha=0.7, label='Ideal Sleep (Max)')
            
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Average Sleep Duration (Hours)', fontsize=12)
            ax.set_title('Your Sleep Pattern for the Year', fontsize=14)
            ax.legend()
            plt.xticks(rotation=45)
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', transparent=True)
        img_buf.seek(0)
        sleep_chart_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        plt.close()
    
    #
    # WATER INTAKE BAR CHART DATA
    #
    
    water_chart_base64 = None
    
    water_records = WaterIntakeRecord.objects.filter(user=user, date__range=[start_date, end_date])
    
    if water_records.exists():
        if selected_month:
            water_data = {}
            date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
            
            for date in date_range:
                water_data[date] = 0  
            
            for record in water_records:
                record_date = record.date.date() if isinstance(record.date, datetime) else record.date
                water_data[record_date] = record.intake_ml
            
            dates = list(water_data.keys())
            intakes = list(water_data.values())
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(dates, intakes, color='#3498db', alpha=0.7)
            
            ax.axhline(y=2000, color='green', linestyle='--', alpha=0.7, label='Recommended Daily Intake (2000ml)')
            
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
            ax.set_xlabel('Day of Month', fontsize=12)
            ax.set_ylabel('Water Intake (ml)', fontsize=12)
            ax.set_title(f'Your Water Intake for {start_date.strftime("%B %Y")}', fontsize=14)
            ax.legend()
            plt.xticks(rotation=45)
        else:
            monthly_water = defaultdict(list)
            
            for record in water_records:
                record_date = record.date.date() if isinstance(record.date, datetime) else record.date
                monthly_water[record_date.month].append(record.intake_ml)
            
            months = []
            avg_water = []
            for month in range(1, 13):
                if monthly_water[month]:
                    avg_water.append(sum(monthly_water[month]) / len(monthly_water[month]))
                else:
                    avg_water.append(0)
                months.append(datetime(this_year, month, 1))
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar([month.strftime('%b') for month in months], avg_water, color='#3498db', alpha=0.7)
            
            ax.axhline(y=2000, color='green', linestyle='--', alpha=0.7, label='Recommended Daily Intake (2000ml)')
            
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Average Water Intake (ml)', fontsize=12)
            ax.set_title('Your Water Intake for the Year', fontsize=14)
            ax.legend()
            plt.xticks(rotation=45)
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', transparent=True)
        img_buf.seek(0)
        water_chart_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        plt.close() 
    
    # Get the list of months for filtering
    months = [(i, datetime(this_year, i, 1).strftime('%B')) for i in range(1, 13)]
    
    return render(request, 'accounts/mood_dashboard.html', {
        'mood_data': mood_data,
        'mood_colors': mood_colors,
        'pie_chart_base64': pie_chart_base64,
        'sentiment_chart_base64': sentiment_chart_base64,
        'sleep_chart_base64': sleep_chart_base64,
        'water_chart_base64': water_chart_base64,
        'selected_month': selected_month,
        'months': months,
        'year': this_year,
        'no_entries': not entries.exists(),
        'no_sleep_records': not sleep_records.exists(),
        'no_water_records': not water_records.exists()
    })

def resources_view(request):
    return render(request, 'accounts/resources.html')

'''
import openai
openai.api_key = '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'

def get_openai_response(user_input):
    try:
        # API call using the new method (for version >=1.0.0)
        response = openai.completions.create(
            model="gpt-3.5-turbo",  
            prompt=user_input,      
            max_tokens=150,          
            temperature=0.7          
        )

        generated_text = response['choices'][0]['text'].strip()

        return generated_text 

    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, there was an issue generating the response."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, something went wrong."

@csrf_exempt
def ai_chatbot(request):
    if request.method == 'POST':
        try:
            # Get the user message from the request
            user_input = request.body.decode('utf-8')
            user_input = user_input.split('=')[1] 

            chatbot_response = get_openai_response(user_input)

            return JsonResponse({'reply': chatbot_response})

        except Exception as e:
            return JsonResponse({'reply': 'Sorry, there was an error processing your request.'}, status=500)

    return JsonResponse({'reply': 'Invalid request method.'}, status=400)
'''