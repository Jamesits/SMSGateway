import asyncio
import logging
from time import sleep
from . import config
from . import smtp_server

logger = logging.getLogger(__name__)
smtp_listeners = []

def main():
    logger.info("Starting")

    # load config
    config.load_user_config("config.toml")
    #print(config.user_config)

    # config logging
    # TODO: user configurable
    logging.basicConfig(level=config.user_config['general']['log_level'] * 10)

    # start SMTP listener
    for ip in config.user_config["general"]["listen"]:
        logger.info(f"Starting SMTP listener on [{ip}]:{config.user_config['general']['smtp_port']}")
        new_listener = smtp_server.SMTPMessageGateway(ip, config.user_config["general"]["smtp_port"])
        new_listener.start()
        smtp_listeners.append(new_listener)

    # start event loop
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logger.info("^C received, quitting...")
    finally:
        for listener in smtp_listeners:
            listener.stop()
    
if __name__ == "__main__":
    main()