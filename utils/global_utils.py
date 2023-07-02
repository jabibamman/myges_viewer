from utils import logger_utils as log
def write_to_console(final_dict):
    """
    TODO: Pas encore bien implémentée
    Affiche le planning dans la console
    :param final_dict:
    :return:
    """
    for key, value in final_dict.items():
        log.get_logger().info(key, ':', value)

