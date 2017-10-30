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
    cursor.execute("SELECT message_id FROM reg_inbox WHERE replied = false ORDER BY created_at ASC")
    unreplied = cursor.fetchall()
    for message_id in [i[0] for i in unreplied]:
        print(message_id)
        message = reddit.inbox.message(message_id)
        if message is not None:
            text = message.body
            if 'karma' in text:
                cursor.execute("SELECT * FROM user_scores WHERE username = %s", (message.author.name,))
                user = cursor.fetchone()
                if user is not None:
                    print(user[1:])
                    post_scores = map(str,user[1:5])
                    comment_scores = map(str,user[5:9])
                    message.reply("your karma till 30/9/2017 ( r/ethereum | r/ethtrader | r/ethdev | r/ethermining ) is posts: {0} & comments: {1}".format(' | '.join(post_scores), ' | '.join(comment_scores)))
                else:
                    message.reply("sorry, your username was not found")
            elif '0x' in text:
                cursor.execute("SELECT id, address FROM users WHERE username = %s", (message.author.name,))
                user = cursor.fetchone()
                if user is not None:
                    address = next(x for x in text.split() if '0x' in x)
                    print(address)
                    if address is not None and is_address(address):
                        cursor.execute("UPDATE users SET address = %s WHERE id = %s", (address, user[0]))
                        if user[1] is not None:
                            message.reply("you have updated your pre-registration ethereum address to: {0}".format(address))
                        else:
                            message.reply("you are now pre-registered with the address: {0}".format(address))
                    else:
                        message.reply("that's doesn't appear to be a valid ethereum address.")
                else:
                    message.reply("sorry, your username was not found")
            else:
                message.reply("sorry, i can't help you")
        cursor.execute("UPDATE reg_inbox SET replied = true WHERE message_id = %s", (message_id,))
        conn.commit()
        print(message_id)
        time.sleep(2)   # no more than 1 reply every 2s
    time.sleep(10)      # only check db for new messages every 10s

conn.close()
