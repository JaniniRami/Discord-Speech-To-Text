import logging

def logger_setup():
    logger = logging.getLogger('discord')
    logger.setLevel(level=logging.INFO)

    handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    logger.addHandler(handler)
    print('[+] Logger setup complete.')

    