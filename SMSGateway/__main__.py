import asyncio
import logging
from time import sleep
import sys
from . import config
from . import smtp_server
from .DbltekSMSServer import DbltekSMSServer

logger = logging.getLogger(__name__)
smtp_listeners = []
DbltekSMSServer_listeners = []

def main():
    logger.info("Starting")

    # load config
    config.load_user_config("config.toml")
    #print(config.user_config)

    # config logging
    logging.basicConfig(level=config.user_config['general']['log_level'] * 10)

    if "listener" not in config.user_config:
        logger.error("No listener defined, quitting")
        sys.exit(-1)

    # start SMTP listener
    if "SMTP" in config.user_config["listener"]:
        for listener in config.user_config["listener"]["SMTP"]:
            logger.info(f"Starting SMTP listener on  [{listener['ip']}]:{listener['port']}")
            new_listener = smtp_server.SMTPMessageGateway(listener['ip'], listener['port'])
            new_listener.start()
            smtp_listeners.append(new_listener)

    if "DbltekSMSServer" in config.user_config["listener"]:
        for listener in config.user_config["listener"]["DbltekSMSServer"]:
            logger.info(f"Starting DbltekSMSServer on [{listener['ip']}]:{listener['port']}")
            new_listener = DbltekSMSServer(listener['ip'], listener['port'])
            new_listener.start()
            DbltekSMSServer_listeners.append(new_listener)

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