#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

import logging
import sqlite3
import telegram

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

helpToDo = ["/help - Gibt eine Liste aller Commands aus",
                "/add % - Fügt einen Eintrag zur ToDo-Liste hinzu",
                "/del % - Löscht einen Eintrag aus der ToDo Liste",
                "/list - Zeigt die komplette Liste an"]

helpKino = ["/help - <b>Liste aller Commands.</b>\n",
                "/addfilm - <b>Hinzufügen eines Films</b>",
                "Bitte gebt hier sowohl den Filmnamen als auch Datum, Uhrzeit und Ort ein.\n"
                "<i>Beispiel: /addfilm Star Wars, 20.03.20, 17:00, M</i>\n",
                "/delfilm - <b>Löschen eines Films</b>",
                "<i>Beispiel: /delfilm Star Wars</i>\n",
                "/filme - <b>Eine Liste aller Filme</b>",
                "<i>Beispiel: /filme</i>\n",
                "/karte - <b>Buchung einer Vorstellung</b>",
                "Hierfür ist es notwendig über den angehefteten Post die Nummer des Filmes herauszusuchen, für den man eine Buchung vorgenommen hat.\n",
                "<i>Beispiel: /karte 1:D5 - Die erste Zahl gibt dabei den Film und die Zeichen hinter dem : den Sitzplatz an. Der Name wird automatisch ergänzt.</i>\n",
                "/delkarte - <b>Löschen einer Buchung</b>",
                "Hierfür ist es notwendig über den angehefteten Post die Nummer des Filmes herauszusuchen, für den man eine Buchung vorgenommen hat.\n",
                "<i>Beispiel: /delkarte 1:D5 - Die erste Zahl gibt dabei den Film und die Zeichen hinter dem : den Sitzplatz an. Der Name wird automatisch ergänzt.</i>\n",
                ]

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):

    output = "Dieser Bot soll helfen, die verschiedenen Buchungen mit der UC zu sammeln und zu verwalten \n\n"
    for s in helpKino:
        text = str(s) + '\n'
        output += text
    context.bot.send_message(chat_id=update.effective_chat.id, text=output, parse_mode=telegram.ParseMode.HTML)


def testdb(update, context):
    """Datenbank testen"""
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    # Create table for todolist
    try: c.execute("CREATE TABLE todoliste (todo text not null)")
    except: print("Datenbank todoliste existiert bereits. Schritt wird übersprungen")

    try: c.execute("CREATE TABLE kinokarten (person TEXT NOT NULL, film TEXT NOT NULL,datum TEXT NOT NULL, uhrzeit TEXT NOT NULL, sitz TEXT NOT NULL)")
    except: print("Datenbank kinokarten existiert bereits. Schritt wird übersprungen")

    try:c.execute("CREATE TABLE film (titel TEXT NOT NULL, datum TEXT ,uhrzeit TEXT)")
    except: print("Datenbank film existiert bereits. Schritt wird übersprungen")

    #c.execute("INSERT INTO film VALUES ('Herr der Ringe', '2020-02-13', '12:14')")
    #except: print("Hat nicht geklappt!")

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
    if update.effective_chat.id == -395510725:
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

        context.bot.send_message(chat_id=update.effective_chat.id, text=output)

def entferneCommandVonText(nachricht):
    entf = str(nachricht)
    output = entf.split(None, 1)
    return output[1]




def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def test(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    #print(update.message)
    schreibeKinokarteInDB("Star Wars")




def addFilm(update, context):
    film = entferneCommandVonText(update.message.text)
    schreibeFilmInDB(film)

def loescheFilm(update, context):
    film = entferneCommandVonText(update.message.text)
    loescheKartenZuFilm(leseFilmausDB(film))
    loescheFilmAusDB(film)



def listFilme(update, context):
    output = "Gebuchte Filme: \n"

    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    c2 = conn.cursor()
    counter = 1
    for row in c.execute("SELECT * FROM film"):
        text = '\n' + str(counter) + ": " + row[0] + '\n'
        output += text
        counter += 1
        for rowKarte in c2.execute("SELECT * FROM kinokarten where film = ? order by sitz", (row[0],)):
            text = '     ' + str(rowKarte[4]) + ' - ' + str(rowKarte[0]) + '\n'
            output += text
    conn.commit()
    conn.close()


    context.bot.pinChatMessage(message_id=context.bot.send_message(chat_id=update.effective_chat.id, text=output).message_id, chat_id=update.effective_chat.id)

def addKarte(update, context):
    film = leseFilmausDB(holeFilmAusKarteInput(update))
    sitz = holeSitzAusKarteInput(update)
    name = update.effective_user.first_name
    schreibeKinokarteInDB(film, sitz, name)

    context.bot.send_message(chat_id=update.effective_chat.id, text=film + ':' + sitz)

def loescheKarte(update, context):
    film = leseFilmausDB(holeFilmAusKarteInput(update))
    sitz = holeSitzAusKarteInput(update)
    name = update.effective_user.first_name
    loescheKinokarteAusDB(film, sitz, name)

def holeFilmAusKarteInput(update):
    txt = str(update.message.text).split(":")
    film = txt[0].split(None, 1)
    return film[1]

def holeSitzAusKarteInput(update):
    txt = str(update.message.text).split(":")
    return txt[1]



def schreibeFilmInDB(film):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    c.execute("INSERT INTO film VALUES (?, 'xxx', 'xxx')", (film,))
    conn.commit()
    conn.close()

def loescheFilmAusDB(filmId):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    titel = leseFilmausDB(filmId)
    c.execute("DELETE FROM film where titel = ?", (titel,))
    conn.commit()
    conn.close()

def leseFilmausDB(filmId):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    counter = 1
    for row in c.execute("SELECT * FROM film"):
        if counter == int(filmId):
            return row[0]
        else:
            counter += 1
    return "Fehler"


def loescheKartenZuFilm(film):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    c.execute("DELETE FROM kinokarten WHERE film=?", (film,))
    conn.commit()
    conn.close()

def schreibeKinokarteInDB(film, sitz, name):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    kinokarte = (name, film, 'xxx', 'xxx', sitz)
    c.execute("INSERT INTO kinokarten VALUES (?,?,?,?,?)", (kinokarte))
    conn.commit()
    conn.close()

def loescheKinokarteAusDB(film, sitz, name):
    conn = sqlite3.connect('savegame.db')
    c = conn.cursor()
    kinokarte = (name, film, sitz)
    c.execute("DELETE FROM kinokarten WHERE person=? AND film=? AND sitz=?", (kinokarte))
    conn.commit()
    conn.close()
#-395510725

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
    dp.add_handler(CommandHandler("test", test))
    dp.add_handler(CommandHandler("addfilm", addFilm))
    dp.add_handler(CommandHandler("filme", listFilme))
    dp.add_handler(CommandHandler("karte", addKarte))
    dp.add_handler(CommandHandler("delfilm", loescheFilm))
    dp.add_handler(CommandHandler("delkarte", loescheKarte))

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