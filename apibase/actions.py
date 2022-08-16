class Action:
    signal = None

    def __init__(self, serializer=None, action=None):
        self.serializer = serializer
        self.extra_fields = {"action": serializer and serializer.view_action or action}

    def save(self, saving):
        instance = saving.save()
        self.dispatch()
        return instance

    def delete(self, deleting):
        deleting.delete()

    def validate(self):
        pass

    def dispatch(self):
        self.signal and self.signal.send(
            sender=self.serializer.instance._meta.model, instance=self.serializer.instance, **self.extra_fields
        )
