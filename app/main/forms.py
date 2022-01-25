from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class NodeForm(FlaskForm):
    ID = StringField('ID', validators=[DataRequired()])
    Label = StringField("Label")
    title = StringField("title")

class LinkForm(FlaskForm):
    ID = StringField('ID', validators=[DataRequired()])
    Type = StringField("Type")
    source = StringField("source_node", validators=[DataRequired()])
    target = StringField("target_node", validators=[DataRequired()])
