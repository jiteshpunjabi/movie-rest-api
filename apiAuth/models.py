from django.db import models
from django.contrib.auth.models import User
import binascii
import os


#authentication
class Token(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=50, primary_key=True)
    created = models.DateField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super(Token,self).save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()
    def __unicode__(self):
        return self.token
    def __str__(self):
        return self.token
