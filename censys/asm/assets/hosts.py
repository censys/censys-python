from .assets import Assets


class Hosts(Assets):
    def __init__(self, *args, **kwargs):
        super().__init__("hosts", *args, **kwargs)
