import praw
import prawcore
import time
import psycopg2

conn_string = "host='localhost' dbname='reddit' user='postgres' password=''"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

reddit = praw.Reddit()

def start():
    try:
        get_messages()
    except prawcore.exceptions.RequestException:
        print("RequestException occurred, restarting...")
        start()

def get_messages():
    for message in reddit.inbox.stream():
        if '!ethreg' in message.body.lower():
            cursor.execute("INSERT INTO reg_inbox (message_id) VALUES (%s) ON CONFLICT (message_id) DO NOTHING", (message.id,))
            conn.commit()

print("streaming inbox")
start()
conn.close()
