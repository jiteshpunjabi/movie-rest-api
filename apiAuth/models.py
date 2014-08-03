from django.db import models
from django.contrib.auth.models import User
import binascii
import os
import hashlib, hmac
from django.conf import settings


#authentication

class TokenManager(models.Manager):
    def check_hash(self, api_key):
        #generate hash of the api_key and then search if it exists in the database....if exists, then it is a valid user
        api_key_hash = hmac.new(str(api_key), getattr(settings,'SECRET_KEY','jiteshpunjabi'), hashlib.sha256).hexdigest().encode()
        try:
            matched_token = self.get_queryset().get(token=api_key_hash)
            if matched_token is not None:
                return matched_token
            else:
                return None
        except Token.DoesNotExist:
            return None

class Token(models.Model):
    objects = TokenManager()
    user = models.ForeignKey(User)
    token = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.reset_token()
        return super(Token, self).save(*args, **kwargs)

    """
    call this method to reset the token
    """
    def reset_token(self):
        # generate token, create hash and store the hash,
        client_token = binascii.hexlify(os.urandom(20)).encode()
        token_hash = hmac.new(str(client_token), getattr(settings,'SECRET_KEY','jiteshpunjabi'), hashlib.sha256).hexdigest().encode()
        self.token = token_hash
        print client_token, token_hash
        return client_token, token_hash

    def check_hash(self, api_key):
        api_key_hash = hmac.new(str(api_key), getattr(settings, 'SECRET_KEY', 'jiteshpunjabi'), hashlib.sha256).hexdigest().encode()
        return self.token == api_key_hash

    def __unicode__(self):
        return self.token
    def __str__(self):
        return self.token
