from django.db import models
from django.contrib.auth.models import User

from instancehistory.history import InstanceHistoryMixin


class Person(InstanceHistoryMixin):

    """ an actual singular human being """

    # for crudbuilder
    search_feilds = ['name']
    tables2_fields = ('name', 'email')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20  # default is 10
    modelform_excludes = ['created_by']

    # model fields
    name = models.CharField(blank=True, max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name
