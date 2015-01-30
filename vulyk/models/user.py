# coding=utf-8
from itertools import chain
from mongoengine import StringField, EmailField, BooleanField, \
    DateTimeField, IntField, ReferenceField, PULL, ListField
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask.ext.mongoengine import Document
import datetime


class Group(Document):
    """
    Class was introduced to serve the permissions purpose
    """
    id = StringField(max_length=100, primary_key=True)
    description = StringField(max_length=200)
    allowed_types = ListField(StringField(max_length=100))

    meta = {'collection': 'groups'}

    def __unicode__(self):
        return self.id

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return u"Group ID: '{id}'. Allowed types: {types}".format(
            id=self.id,
            types=self.allowed_types)


class User(Document, UserMixin):
    username = StringField(max_length=200)
    password = StringField(max_length=200, default='')
    name = StringField(max_length=100)
    email = EmailField()
    active = BooleanField(default=True)
    admin = BooleanField(default=False)
    groups = ListField(ReferenceField(Group,
                                      reverse_delete_rule=PULL,
                                      default=None))
    last_login = DateTimeField(default=datetime.datetime.now)
    processed = IntField(default=0)

    def is_active(self):
        return self.active

    def is_admin(self):
        return self.admin or False

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def is_eligible_for(self, task_type):
        """
        Check that user is authorized to work with this tasks type

        :param task_type: Tasks type name
        :type task_type: str | unicode

        :return: True if user is eligible

        :raises: AssertionError - if no `task_type` specified
        """
        assert task_type, "Empty parameter `task_type` passed"

        return task_type in set(chain((g.allowed_types for g in self.groups)))


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"
