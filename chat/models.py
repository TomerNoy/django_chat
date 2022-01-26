from django.contrib.auth import get_user_model
from django.db import models

Usr = get_user_model()


class Msg(models.Model):
    usr = models.TextField()
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usr.name

    @staticmethod
    def last_msgs():
        return Msg.objects.order_by('time').all()[:10]
