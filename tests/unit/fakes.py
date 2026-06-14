class FakeStorage:
    def __init__(self):
        self.fs = {}

    async def save(self, key, value):
        self.fs[str(key)] = value

    async def delete(self, key):
        del self.fs[str(key)]

    def __len__(self):
        return len(self.fs)

    def __contains__(self, item):
        return str(item) in self.fs