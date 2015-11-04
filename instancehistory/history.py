import pickle
import collections
from django.db.models import signals, Model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


# from instancehistory.signals import post_change
from instancehistory.models import InstanceStateHistory
from instancehistory.signals import get_request

SAVE = 0
DELETE = 1


class InstanceHistoryMixin(Model):
    history = GenericRelation(InstanceStateHistory)

    def __init__(self, *args, **kwargs):
        super(InstanceHistoryMixin, self).__init__(*args, **kwargs)

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
        """Create state for each instance"""

        request = get_request()

        InstanceStateHistory.objects.create(
            content_object=self,
            changed_by=request.user
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
    def latest_state_created_by(self):
        """Who created last history"""
        return self.history.all().latest('id').changed_by

    @property
    def all_history(self):
        """
        Returns all history objects for the specific instance
        """
        return self.history.all()

    @property
    def current_state(self):
        """
        Returns a ``field -> value`` dict of the current state of the instance.
        """
        return self.history.all().latest('id')

    @property
    def changes(self):
        super_dict = collections.defaultdict(set)
        all_history = self.all_history

        for history_obj in all_history:
            for field in history_obj._meta.fields:
                super_dict[field.name].add(getattr(history_obj, field.name))
        return dict(super_dict)


def _post_save(sender, instance, **kwargs):
    instance._save_state(new_instance=False, event_type=SAVE)


def _post_delete(sender, instance, **kwargs):
    instance._save_state(new_instance=False, event_type=DELETE)
