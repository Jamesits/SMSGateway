import logging
import os
import typing

from SMSGateway import config
from SMSGateway.args import parse_args
from SMSGateway.generic_event_queue import PythonQueueBasedEventQueue
from SMSGateway.generic_listener import GenericListener
from SMSGateway.generic_vertex import GenericVertex
from SMSGateway.mapping import mapping_mapping
from SMSGateway.utils import find_first_existing_file

logger = logging.getLogger(__name__)
vertices: typing.List[GenericVertex] = []
edges: typing.List[typing.Tuple[GenericVertex, GenericVertex]] = []


def init_vertex(vertex_type: str, local_config: typing.Dict[str, any], global_config: any) -> GenericVertex:
    alias = local_config['alias']
    object_type = local_config['type'].lower()
    logger.info(f"Initializing vertex {vertex_type}/{object_type} {alias}")

    mapping = mapping_mapping[vertex_type.lower()]
    new_vertex = mapping[object_type](
        alias,
        object_type,
        local_config,
        global_config,
    )

    vertices.append(new_vertex)
    return new_vertex


def init_edge(vertex_from_alias: str, vertex_to_alias: str):
    logger.info(f"Initializing edge {vertex_from_alias} -> {vertex_to_alias}")
    # find the vertices we need
    vertex_from = None
    vertex_to = None
    for vertex in vertices:
        if vertex.alias == vertex_from_alias:
            vertex_from = vertex
            continue
        if vertex.alias == vertex_to_alias:
            vertex_to = vertex
            continue

    if (vertex_from is None) or (vertex_to is None):
        logger.error(f"Incorrect edge definition")
        return

    # save edge information in global variable
    edges.append((vertex_from, vertex_to))

    # save edge information in every node
    vertex_from.add_out_edge(vertex_to)
    vertex_to.add_in_edge(vertex_from)

    return vertex_from, vertex_to


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s|%(name)-26s[%(levelname)s] %(message)s'
    )
    logger.info("SMSGateway server starting")

    # parse arguments
    config.args = parse_args()

    user_config_file_path = config.args.config
    if len(user_config_file_path) == 0:
        user_config_file_path = find_first_existing_file([
            "/etc/smsgateway/config.toml",
            "./config.toml",
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "config.toml"),
        ])
    if len(user_config_file_path) == 0:
        logger.error("Unable to find a config file, please manually set --config command line argument")
        raise SystemExit(-1)

    # load config
    logger.info(f"Loading config file from {user_config_file_path}")
    config.load_user_config(user_config_file_path)

    # config logging
    logging.basicConfig(level=config.user_config['general']['log_level'] * 10)

    # initialize an event queue
    config.queue = PythonQueueBasedEventQueue()

    # initialize all the listeners
    if 'listener' in config.user_config:
        for local_config in config.user_config['listener']:
            new_listener = init_vertex('listener', local_config, config)
            assert isinstance(new_listener, GenericListener)
            new_listener.start()

    # initialize sinks
    if 'sink' in config.user_config:
        for local_config in config.user_config['sink']:
            init_vertex('sink', local_config, config)

    # initialize filters
    if 'filter' in config.user_config:
        for local_config in config.user_config['filter']:
            init_vertex('filter', local_config, config)

    # initialize sources
    if 'source' in config.user_config:
        for local_config in config.user_config['source']:
            init_vertex('source', local_config, config)

    # create edges
    if 'routes' in config.user_config:
        for vertex_from_alias in config.user_config['routes'].keys():
            for vertex_to_alias in config.user_config['routes'][vertex_from_alias]:
                init_edge(vertex_from_alias, vertex_to_alias)

    logger.info("Config file parsed")

    # start event loop
    logger.info("Starting event loop")
    try:
        config.queue.event_loop_sync()
    except KeyboardInterrupt:
        logger.info("^C received, quitting...")
    finally:
        for vertex in vertices:
            if isinstance(vertex, GenericListener):
                vertex.stop()

    logger.info("event loop stopped")


if __name__ == "__main__":
    main()
