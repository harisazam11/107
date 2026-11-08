APPENDICES

APPENDIX A
CODE

import os
from os import listdir
from os.path import isfile, join
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "D:\key.json"
from google.cloud import vision
from my_timer import my_timer
import time

def detect_text(path):
    client = vision.ImageAnnotatorClient()
    with open(path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    ocr_text = []
    for text in texts:
        ocr_text.append(f"\r\n{text.description}")
    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return texts[0].description

from nltk.sentiment import SentimentIntensityAnalyzer

import nltk
sia = SentimentIntensityAnalyzer()
def analyze_sentiment_with_reasons(text):
    print(f"Analyzing sentiment for: {text}")
    scores = sia.polarity_scores(text)

    words = nltk.word_tokenize(text)
    word_scores = {word: sia.polarity_scores(word) for word in words}

    positive_words = [word for word, score in word_scores.items() if score["compound"] > 0.05]
    negative_words = [word for word, score in word_scores.items() if score["compound"] < -0.05]
    neutral_words = [word for word, score in word_scores.items() if -0.05 <= score["compound"] <= 0.05]

    sentiment = (
        "Positive" if scores["compound"] > 0.05 else
        "Negative" if scores["compound"] < -0.05
        else
        "Neutral"
    )

    print(f"Sentiment: {sentiment}")
    print(f"Positive Words: {positive_words}")
    print(f"Negative Words: {negative_words}")
    print(f"Neutral Words: {neutral_words}")

    return sentiment, positive_words, negative_words, neutral_words

def insert_data(image_path, text, sentiment, positive_words, negative_words, neutral_words):
    # Connect to SQLite database
    conn = sqlite3.connect('ocr_sentiment.db')
    cursor = conn.cursor()

    # Insert data into the table
    cursor.execute('''
        INSERT INTO image_data (image_name, image_text, sentiment, positive_words, negative_words, neutral_words)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (image_path, text, sentiment, ', '.join(positive_words), ', '.join(negative_words), ', '.join(neutral_words)))

    conn.commit()
    conn.close()

from tkinter import Tk, filedialog
# bro, how to run this ?

# Before showing the dialog
root = Tk()
root.withdraw() # Hide the root tkinter window

image_path = filedialog.askopenfilename(
    title="Select an Image",
    filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")],
)
root.destroy() # Close the hidden tkinter window

# Extract text from image using OCR
text = detect_text(image_path)

# Clean the text (remove new lines, etc.)
text = text.split('\n')
text = ' '.join(text)

# Analyze sentiment
sentiment, positive_words, negative_words, neutral_words = analyze_sentiment_with_reasons(text)

# Insert data into the SQLite database
# insert_data(image_path, text, sentiment, positive_words, negative_words, neutral_words)

# Optional: Print the inserted data (for debugging)
print(f"Data inserted: {image_path} | Sentiment: {sentiment}")

def view_database():
    # Connect to SQLite database
    conn = sqlite3.connect('ocr_sentiment.db')
    cursor = conn.cursor()

    # Fetch all rows from the table
    cursor.execute('SELECT * FROM image_data')
    rows = cursor.fetchall()

    # Display all rows
    for row in rows:
        print(f"ID: {row[0]}, Image: {row[1]}, Sentiment: {row[3]}")
        print(f"Text: {row[2]}")
        print(f"Positive Words: {row[4]}")
        print(f"Negative Words: {row[5]}")
        print(f"Neutral Words: {row[6]}")

print("-" * 40)

conn.close()

# Optional: Call view_database() to view the entries
view_database()
text = "now we are 555 mmmm jjjj jjjj jjjj worst best"
sentiment, positive_words, negative_words, neutral_words = analyze_sentiment_with_reasons(text)

import sqlite3

# Function to initialize the database and create a table
def init_db():
    conn = sqlite3.connect('ocr_sentiment.db') # Create or open the database file
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT NOT NULL,
            image_text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            positive_words TEXT,
            negative_words TEXT,
            neutral_words TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()