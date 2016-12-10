from django.db import models
from django.contrib.auth.models import User
# import django.contrib.postgres.fields as pg_fields

# TURN_STATES = (
#     ('blue_give', 'Blue Team to give clue'), ('blue_guess', 'Blue Team to guess'),
#     ('red_give', 'Red Team to give clue'), ('red_guess', 'Red Team to guess')
# )

# class Word(models.Model):
#     '''A word can be reused across games'''
#     text = models.CharField(max_length=200)
#     word_set = models.ForeignKey(WordSet, default=1)
#     color = models.CharField(
#             max_length=5,
#             choices=COLOR_CHOICES,
#             default='grey'
#         )

#     def __unicode__(self):
#         return self.text
