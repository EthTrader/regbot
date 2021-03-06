import praw
import time
import psycopg2
from eth_utils.address import is_address
from string import Template

conn_string = "host='localhost' dbname='reddit' user='postgres' password=''"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

reddit = praw.Reddit()

while True:
    cursor.execute("SELECT comment_id FROM reg_comments WHERE replied = false ORDER BY created_at ASC")
    unreplied = cursor.fetchall()
    for comment_id in [i[0] for i in unreplied]:
        comment = reddit.comment(comment_id)
        if comment.author is None:
            print(comment_id, " was removed")
            continue
        text = comment.body
        if 'karma' in text:
            cursor.execute("SELECT sum(score) FROM content WHERE author = %s", (comment.author.name,))
            user = cursor.fetchone()
            if user is not None:
                print(comment.author.name)
                comment.reply("your karma till 30/1/2018 is posts: {0}".format(user[0]))
            else:
                comment.reply("sorry, your username was not found")
        elif '0x' in text:
            cursor.execute("SELECT id, address FROM users WHERE username = %s", (comment.author.name,))
            user = cursor.fetchone()
            if user is not None:
                address = next(x for x in text.split() if '0x' in x)
                print(address)
                if address is not None and is_address(address):
                    cursor.execute("UPDATE users SET address = %s WHERE id = %s", (address, user[0]))
                    if user[1] is not None:
                        comment.reply("you have updated your pre-registration ethereum address to: {0}".format(address))
                    else:
                        comment.reply("you are now pre-registered with the address: {0}".format(address))
                else:
                    comment.reply("that's doesn't appear to be a valid ethereum address.")
            else:
                comment.reply("sorry, your username was not found")
        else:
            comment.reply("sorry, i can't help you")
        cursor.execute("UPDATE reg_comments SET replied = true WHERE comment_id = %s", (comment_id,))
        conn.commit()
        print(comment_id)
        time.sleep(2)   # no more than 1 reply every 2s
    time.sleep(10)      # only check db for new comments every 10s

conn.close()
