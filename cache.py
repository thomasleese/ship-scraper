import json


class Cache(dict):
    def __init__(self):
        super().__init__()

        self._stop_saving = False

        self.load()

    def load(self):
        self._stop_saving = True

        try:
            with open('cache.json') as file:
                for key, value in json.loads(file.read()).items():
                    self[key] = value
        except FileNotFoundError:
            pass

        self._stop_saving = False

    def save(self):
        with open('cache.json', 'w') as file:
            file.write(json.dumps(self, indent=2))

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if not self._stop_saving:
            self.save()

    def make_key(self, args):
        return '.'.join(str(arg) for arg in args)

    def get(self, *args):
        return self[self.make_key(args)]

    def has(self, *args):
        key = self.make_key(args)
        return key in self

    def set(self, *args):
        value = args[-1]
        keys = args[:-1]
        self[self.make_key(keys)] = value
