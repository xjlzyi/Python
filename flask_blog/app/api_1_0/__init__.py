# -*- coding:utf-8 -*-
#!/usr/bin/env python

from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, comments, posts, users, errors