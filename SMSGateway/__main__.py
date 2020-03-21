import logging
import sys
import typing
from time import sleep

from . import config
from .DbltekSmsListener import DbltekSMSListener
from .IListener import IListener
from .SMTPListener import SMTPListener

logger = logging.getLogger(__name__)
listeners: typing.List[IListener] = []

listener_registration = {
    "SMTP": SMTPListener,
    "DbltekSmsListener": DbltekSMSListener,
    # "SMPPListener": None,
}


def main():
    logger.info("Starting")

    # load config
    config.load_user_config("config.toml")

    # config logging
    logging.basicConfig(level=config.user_config['general']['log_level'] * 10)

    if "listener" not in config.user_config:
        logger.error("No listener defined, quitting")
        sys.exit(-1)

    for l_type in config.user_config["listener"]:
        for l_config in config.user_config["listener"][l_type]:
            if l_type not in listener_registration:
                logger.warning(f"Unknown listener type {l_type}")
                continue
            logger.info(f"Starting {l_type} listener on [{l_config['ip']}]:{l_config['port']}")
            new_listener = listener_registration[l_type](l_config, config)
            listeners.append(new_listener)
            new_listener.start()

    # start event loop
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logger.info("^C received, quitting...")
    finally:
        for listener in listeners:
            listener.stop()


if __name__ == "__main__":
    main()
