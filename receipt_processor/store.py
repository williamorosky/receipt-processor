import threading


class ReceiptStore:
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()

    def save(self, receipt_id: str, points: int):
        with self.lock:
            self.store[receipt_id] = points

    def get(self, receipt_id: str):
        with self.lock:
            return self.store.get(receipt_id)


receipt_store = ReceiptStore()
