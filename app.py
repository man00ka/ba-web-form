from flask import Flask, render_template, request, session
import random, os, json
import smtplib
from email.mime.text import MIMEText
import numpy as np 
import psycopg2  # Handling of postgres SQL database
from psycopg2 import Error
from psycopg2.extensions import parse_dsn
from urllib.parse import urlparse  # To parse POSGRES_URL
from pprint import pprint

app = Flask(__name__)

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_FROM = os.environ.get('EMAIL_FROM')
EMAIL_TO = os.environ.get('EMAIL_TO')
APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY")

# Set up session to handle variables throughout several functions:
app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

DATABASE_URL = os.environ.get("POSTGRES_URL")

## CREATE DB CONNECTION ##
def create_connection():
    p = urlparse(DATABASE_URL)
    pg_connection_dict = {
    'dbname': "verceldb",
    'user': p.username,
    'password': p.password,
    'port': os.environ.get("POSTGRES_PORT"),
    'host': os.environ.get("POSTGRES_HOST")
    }
    # pprint(pg_connection_dict, sort_dicts=False)
    """Create a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(**pg_connection_dict)
        return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None


## INITIALIZE DATABASE ##
# def initialize_database():
#     """Initialize the database tables."""
#     try:
#         connection = create_connection()
#         cursor = connection.cursor()
# 
#         # Create text_infos table if not exists
#         create_table_query = """
#         CREATE TABLE IF NOT EXISTS text_infos (
#             id SERIAL PRIMARY KEY,
#             file_name VARCHAR(255) UNIQUE,
#             headline VARCHAR(255),
#             target_length INTEGER,
#             n_times_summarized INTEGER
#         )
#         """
#         cursor.execute(create_table_query)
#         connection.commit()
# 
#         # Insert initial data into text_infos table
#         initial_data = [
#             ("ABBA.txt", "Text: ABBA", 180, 0),
#             ("Buch.txt", "Text: Buch", 225, 0),
#             ("Chor.txt", "Text: Chor", 150, 0),
#             ("Faultier.txt", "Text: Faultier", 280, 0),
#             ("Globus.txt", "Text: Globus", 180, 0)
#             # Add more tuples as needed
#         ]
#         insert_query = """
#         INSERT INTO text_infos (file_name, headline, target_length, n_times_summarized)
#         VALUES (%s, %s, %s, %s)
#         """
#         cursor.executemany(insert_query, initial_data)
#         connection.commit()
# 
#         cursor.close()
#         connection.close()
#     except Error as e:
#         print(f"Error initializing the database: {e}")


## FETCH FILENAME ##
def fetch_file_names():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Fetch all available filenames
        file_name_query = """SELECT file_name FROM text_infos"""
        cursor.execute(file_name_query)
        lFileNames = [row[0] for row in cursor.fetchall()]
        return lFileNames
    except Error as e:
        print(f"Error fetching file names: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


## FETCH N_TIMES_SUMMARIZED ##
def fetch_n_times_summarized():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Fetch all available filenames
        query = """SELECT n_times_summarized FROM text_infos"""
        cursor.execute(query)
        lNTimesSummarized = [row[0] for row in cursor.fetchall()]
        return lNTimesSummarized
    except Error as e:
        print(f"Error fetching file names: {e}")
        return None
    finally:
        cursor.close()
        connection.close()      



## FETCH TEXT_INFO ##
def fetch_text_info(file_name):
    try:
        """Fetch text information from the database based on the file_name."""
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT headline, target_length, n_times_summarized FROM text_infos WHERE file_name = %s", (file_name,))
        text_info = cursor.fetchone()
        return text_info
    except Error as e:
        print(f"Error fetching text info from database: {e}")
        return None
    finally:
        cursor.close()
        connection.close()



## UPDATE DATABASE ##
def update_text_info(file_name, headline, target_length, n_times_summarized):
    """Update or insert text information into the database."""
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Check if file_name already exists in the table
        cursor.execute("SELECT * FROM text_infos WHERE file_name = %s", (file_name,))
        existing_text_info = cursor.fetchone()

        if existing_text_info:
            # Update existing record
            update_query = """
            UPDATE text_infos
            SET n_times_summarized = %s
            WHERE file_name = %s
            """
            cursor.execute(update_query, (n_times_summarized, file_name))
        else:
            # Insert new record
            insert_query = """
            INSERT INTO text_infos (file_name, headline, target_length, n_times_summarized)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (file_name, headline, target_length, n_times_summarized))

        connection.commit()
        cursor.close()
        connection.close()

    except Error as e:
        print(f"Error updating text info in the database: {e}")






# Die Datenbank wird initialisiert, falls sie noch nicht existiert.
# initialize_database()


# Calculate weights for random text sampling
lNTimesSummarized = fetch_n_times_summarized()
lNTimesSummarized = np.array(lNTimesSummarized)
weights = 1/(lNTimesSummarized + 1)  # Invert the weights
weights = weights/len(weights)  # Normalize the weights

# text directory:
text_dir = "./text_files"
img_dir = "./static/images"
my_image = [img for img in os.listdir(img_dir) if img=="ich.jpeg"][0]

@app.route('/')
def index():
    # Choose a random text considering weights
    lFileNames = fetch_file_names()
    print(weights)
    file_name = random.choices(lFileNames, weights=weights)[0]
    # also set the file name in session to make it available to the 
    # submit function without routing it through the index.html. This
    # should also be thread safe and therefor production friendly:
    session["file_name"] = file_name
    # Die Headline für den Text:
    text_infos = fetch_text_info(file_name)
    text_headline = text_infos[0]
    target_length = text_infos[1]
    n_times_summarized = text_infos[2]
    session["text_headline"] = text_headline
    session["target_length"] = target_length
    session["n_times_summarized"] = n_times_summarized
    # Ziellänge für die Zusammfassung (als orientierung):
    # Den Text aus Datei lesen:
    with open(os.path.join(text_dir, file_name)) as f:
        text_description = f.read()
    return render_template(
        'index.html',
        text_description=text_description,
        text_headline=text_headline,
        target_length=target_length,
        my_image=my_image
        )

@app.route('/submit', methods=['POST'])
def submit():
    # Get Variables from Session:
    file_name = session.get("file_name", None)
    text_headline = session.get("text_headline", None)
    target_length = session.get("")
    n_times_summarized = session.get("n_times_summarized", None)

    text = request.form['text']
    # Increment n_times_summarized in database
    n_times_summarized += 1
    update_text_info(file_name, text_headline, target_length, n_times_summarized)
    
    # Process the submitted text (You can save it to a database or perform any other action here)
    # Via E-Mail versenden:
    msg = MIMEText(
        f"\n{text_headline}\n Zusammenfassung Nr.: {n_times_summarized}  \n\n" + text
        )
    msg['Subject'] = 'Submitted Text'
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        server.quit()
    except Exception as e:
        return f"Failed to send email: {e}"

    return "Text erfolgreich eingereicht.<br>Vielen Dank!"

if __name__ == '__main__':
    app.run(debug=True)
