import logging

log = logging.getLogger(__name__)




class OrderRepository:
    def __init__(self, session):
        self.session = session

    async def get_expired_pending_order_ids(self):
        pass
