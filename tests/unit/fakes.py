from domain import NotFoundError


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


class FakeDB:
    def __init__(self):
        self.storage = []

    async def create(self, obj):
        obj.id = len(self.storage) + 1
        self.storage.append(obj)
        return obj

    async def read_one(self, model, with_raise=False, **kwargs):
        kwargs.pop("with_for_update", None)
        kwargs.pop("loaded", None)

        obj = next(
            (
                item
                for item in self.storage
                if all(getattr(item, k, None) == v for k, v in kwargs.items())
            ),
            None,
        )

        if obj is not None:
            return obj

        if with_raise:
            raise NotFoundError("Not found in FakeDB")
        return None


class FakeUoW:
    def __init__(self):
        self.db = FakeDB()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def fake_name_calculate(*args, **kwargs):
    return "name"
