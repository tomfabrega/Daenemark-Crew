#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

import logging
import sqlite3

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

commands = ["/help - Gibt eine Liste aller Commands aus",
                "/add % - Fügt einen Eintrag zur ToDo-Liste hinzu",
                "/del % - Löscht einen Eintrag aus der ToDo Liste",
                "/list - Zeigt die komplette Liste an"]

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):

    output = ""
    counter = 1
    for s in commands:
        text = str(counter) + ": " + str(s) + '\n'
        output += text
        counter += 1
    update.message.reply_text(output)

def testdb(update, context):
    """Datenbank testen"""
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    # Create table
    try: c.execute('''CREATE TABLE todoliste (todo text not null)''')
    except: print("Datenbank existiert bereits. Schritt wird übersprungen")

    conn.commit()
    conn.close()

def addToDo(update, context):
    """Einen Eintrag der Liste hinzufügen"""
    todo = entferneCommandVonText(update.message.text)
    schreibeTodoInDB(todo)

def deleteToDo(update, context):
    todo = entferneCommandVonText(update.message.text)
    entferneTodoEintrag(todo)

def entferneTodoEintrag(todo):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    c.execute("DELETE FROM todoliste WHERE todo=?", (todo,))
    conn.commit()
    conn.close()

def schreibeTodoInDB(todo):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    c.execute("INSERT INTO todoliste VALUES (?)", (todo,))
    conn.commit()
    conn.close()

def writeList(update, context):
    """Schreibe den Inhalt der Liste in den Chat"""
    output = "Todo-Liste der Fantastischen-Vier: \n"

    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    counter = 1

    for row in c.execute('SELECT * FROM todoliste'):

        text = str(counter) + ": " + str(row[0]) + '\n'
        output += text
        counter += 1
    conn.commit()
    conn.close()

    update.message.reply_text(output)

def entferneCommandVonText(nachricht):
    entf = str(nachricht)
    output = entf.split(None, 1)
    return output[1]

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)





def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("961938913:AAHhmRDlMNUFKUSMloCMpVHibHMMKsQTNZU", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("db", testdb))
    dp.add_handler(CommandHandler("list", writeList))
    dp.add_handler(CommandHandler("add", addToDo))
    dp.add_handler(CommandHandler("del", deleteToDo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()