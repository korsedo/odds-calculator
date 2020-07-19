from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import re

# Enable logging
logging.basicConfig(filename='./odds_convector.log', filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def lay_calc(odds):
    backOdds = round(1 + 1 / (odds - 1), 2)
    backOddsWithCommission = round((backOdds - 1) * 0.935 + 1, 2)
    message = f'back odds: {backOdds}\n'\
        f'with commission: {backOddsWithCommission}'

    return message


def surebet_calc(request):
    odds = request.split()
    odds = list(map(float, odds))
    if len(odds) <= 1 or len(odds) > 3:
        return 'Incorrect format'
    margin = 0
    for price in odds:
        margin += 1/price
    margin = round((margin - 1) * -100, 2)
    if len(odds) == 2:
        profit = round((odds[0] - 1) * 100 - odds[0] * 100 / odds[1], 2)
        return f"margin: {margin:+}% profit: {profit:+}%"
    else:
        return f"margin: {margin:+}%"
	
	
def echo(bot, update):
    """Echo the user message."""
    request = str(update.message.text).replace(',', '.')
    if re.match(r'[0-9,. ]+$', request):
        margin = surebet_calc(request)
        update.message.reply_text(margin)
    else:
        request = request.split()
        side = request[0].strip()
        raw_odds = request[1].strip()
        odds = float(raw_odds)
        if side.lower() == 'home':
            update.message.reply_text(round((odds-1)*2.5+1, 2))
        elif side.lower() == 'away':
            update.message.reply_text(round((odds-1)/2.5+1, 2))
        elif side.lower() == 'lay':
            update.message.reply_text(lay_calc(odds))
        else:
            update.message.reply_text("""Please, "Home" or "Away" or "Lay".""")

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

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
