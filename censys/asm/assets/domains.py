from .assets import Assets


class Domains(Assets):
    def __init__(self, *args, **kwargs):
        super().__init__("domains", *args, **kwargs)

    # TODO: Subdomains
