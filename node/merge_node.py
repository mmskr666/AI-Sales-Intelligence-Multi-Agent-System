from state.SalesState import SalesState
from tools.logger import logger


def merge_node(state:SalesState):
    logger.info("👉 Merge Node")
    return {
        "merge_ready": True
    }
