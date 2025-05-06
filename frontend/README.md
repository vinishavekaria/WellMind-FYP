# WellMind

WellMind is a Django-based wellness web application designed to help users improve their mental well-being. It features daily mood tracking, wellness tips, habit tracking (water intake, sleep), motivational quotes, and mood-based music suggestions using playlists.

---

### Key Features

- Mood journal with sentiment analysis  
- AI-powered wellness tips  
- Water intake and sleep tracking  
- Daily inspirational quotes  
- To-do task management  
- Mood-based music suggestions 
- Personalised dashboard on login  

---

### 🔧 Project Setup Instructions

1. **Open a terminal or command prompt**  
   Navigate to the project folder:

   ```bash
   cd "C:\Users\Vinisha Vekaria\Documents\project\project"

2. **Install required Python libraries**  
   Run the following command to install the necessary packages:

   ```bash
   pip install django matplotlib textblob spacy nltk

3. **Download NLP Data**

    ```bash
    python -m textblob.download_corpora
    python -m nltk.downloader punkt averaged_perceptron_tagger
    python -m spacy download en_core_web_md

4. **Apply database migrations**

    ```bash
    python manage.py makemigrations
    python manage.py migrate

5. **Run Development Server**

    ```bash
    python manage.py runserver

6. **Access the django admin database**

    ```bash
    Username:vinisha_vekaria
    Password:chillipaneer

7. **Example user credentials**
    Login using these details to see the users data 

    ```bash
    Username: vinishavekaria
    Password: Spongebob1!
