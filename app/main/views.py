from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from . import main
from .forms import ChangeForm
from flask_login import login_required
from datetime import datetime


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', current_time=datetime.utcnow())
