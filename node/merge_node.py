from state.SalesState import SalesState
from tools.logger import logger


def merge_node(state:SalesState):
    logger.debug("👉 Merge Node")
    return {
        "merge_ready": True
    }
