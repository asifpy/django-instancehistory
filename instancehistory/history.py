import pickle
import datetime
import collections
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType

from instancehistory.signals import post_change
from instancehistory.models import InstanceStateHistory

SAVE = 0
DELETE = 1

class HistoryMixin(object):
    def __init__(self, *args, **kwargs):
        super(HistoryMixin, self).__init__(*args, **kwargs)

        signals.post_save.connect(
            _post_save, sender=self.__class__,
            dispatch_uid='django-changes-%s' % self.__class__.__name__
        )
        
        signals.post_delete.connect(
            _post_delete, sender=self.__class__,
            dispatch_uid='django-changes-%s' % self.__class__.__name__
        )

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)

    def _save_state(self, new_instance=False, event_type='save'):
        
        InstanceStateHistory.objects.create(
            state=pickle.dumps(self.fields_values()),
            content_type=self.content_type,
            object_id=self.id
            )

    def fields_values(self):
        """
        Prepare a ``field -> value`` dict of the current state of the instance.
        """
        field_names = set()
        [field_names.add(f.name) for f in self._meta.local_fields]
        [field_names.add(f.attname) for f in self._meta.local_fields]
        return dict([(field_name, getattr(self, field_name)) for field_name in field_names])

    @property
    def history(self):
        """
        Returns all the state history objects
        """
        return InstanceStateHistory.objects.filter(
            object_id=self.id,
            content_type=self.content_type,
            )

    @property
    def current_state(self):
        """
        Returns a ``field -> value`` dict of the current state of the instance.
        """
        state = self.history.latest('id').state
        return pickle.loads(state)

    @property
    def changes(self):
        states = self.history.values_list('state', flat=True)
        pickled_states = [pickle.loads(state) for state in states]

        super_dict = collections.defaultdict(set)
        for d in pickled_states:
            for k, v in d.iteritems():
                super_dict[k].add(v)
        return dict(super_dict)

def _post_save(sender, instance, **kwargs):
    instance._save_state(new_instance=False, event_type=SAVE)


def _post_delete(sender, instance, **kwargs):
    instance._save_state(new_instance=False, event_type=DELETE)
