from bot import bot

if __name__ == '__main__':
    try:
        bot.activate()
    except Exception as e:
        print(e)