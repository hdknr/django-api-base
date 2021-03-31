class Action:
    signal = None

    def __init__(self, serializer):
        self.serializer = serializer
        self.extra_fields = {}

    def validate(self):
        pass

    def dispatch(self):
        self.signal and self.signal.send(
            sender=self.serializer.instance._meta.model_class,
            instance=self.serializer.instance,
            **self.extra_fields
        )