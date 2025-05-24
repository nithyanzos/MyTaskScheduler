from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from task_manager_app.app.models import Category, User # User is already imported

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=25), 
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers, dots or underscores')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('staff', 'Staff'), ('manager', 'Manager'), ('admin', 'Admin')],
                       validators=[DataRequired()])
    reports_to = QuerySelectField('Reports To (Manager)', 
                                  query_factory=lambda: User.query.filter(User.role.in_(['manager', 'admin'])).all(), 
                                  get_label='username', allow_blank=True, blank_text='-- Select Manager --',
                                  validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class EditUserForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=25), 
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers, dots or underscores')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('staff', 'Staff'), ('manager', 'Manager'), ('admin', 'Admin')],
                       validators=[DataRequired()])
    reports_to = QuerySelectField('Reports To (Manager)', 
                                  query_factory=lambda: User.query.filter(User.role.in_(['manager', 'admin'])).all(), 
                                  get_label='username', allow_blank=True, blank_text='-- Select Manager --',
                                  validators=[Optional()])
    submit = SubmitField('Update User')

# Ensure date is imported for CreateRecurringTaskForm default
from datetime import date

class CreateRecurringTaskForm(FlaskForm):
    base_task_title = StringField('Base Task Title', validators=[DataRequired(), Length(min=3, max=200)])
    base_task_description = TextAreaField('Base Task Description', validators=[Optional()])
    base_task_priority = SelectField('Base Task Priority', 
                                     choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], 
                                     default='Medium', validators=[DataRequired()])
    base_task_category = QuerySelectField('Base Task Category', 
                                          query_factory=lambda: Category.query.all(), 
                                          get_label='name', allow_blank=True, blank_text='-- Select Category --',
                                          validators=[Optional()])
    assigned_to = QuerySelectField('Assign to User', 
                                   query_factory=lambda: User.query.all(), 
                                   get_label='username', allow_blank=True, blank_text='-- Assign to User --',
                                   validators=[Optional()])
    recurrence_rule = SelectField('Recurrence Rule', choices=[
                                    ('daily', 'Daily'),
                                    ('weekly', 'Weekly (on creation day)'),
                                    ('biweekly', 'Bi-weekly (on creation day)'),
                                    ('monthly_day', 'Monthly (on same day of month)')
                                  ], validators=[DataRequired()])
    start_date = DateField('Start Date', default=date.today, validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    submit = SubmitField('Create Recurring Pattern')

class SendCategoryEmailForm(FlaskForm):
    category = QuerySelectField('Category', 
                                query_factory=lambda: Category.query.all(), 
                                get_label='name', allow_blank=False,
                                validators=[DataRequired()])
    send_to_dl = BooleanField('Send to Group Distribution List', default=False)
    send_to_assignees = BooleanField('Send to Individual Assignees', default=True)
    subject = StringField('Email Subject', 
                          validators=[DataRequired(), Length(max=200)], 
                          default="Task Summary for Category: ")
    custom_message = TextAreaField('Additional Message (Optional)')
    submit = SubmitField('Send Category Email')

class CreateTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description')
    due_date = DateField('Due Date', validators=[Optional()])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
                           validators=[DataRequired()])
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), 
                                get_label='name', allow_blank=True, blank_text='-- Select Category --',
                                validators=[Optional()])
    assigned_to = QuerySelectField('Assign to User', query_factory=lambda: User.query.all(),
                                   get_label='username', allow_blank=True, blank_text='-- Assign to User --',
                                   validators=[Optional()])
    submit = SubmitField('Create Task')

class EditTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description')
    due_date = DateField('Due Date', validators=[Optional()])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
                           validators=[DataRequired()])
    status = SelectField('Status', choices=[('To Do', 'To Do'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
                         validators=[DataRequired()])
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), 
                                get_label='name', allow_blank=True, blank_text='-- Select Category --',
                                validators=[Optional()])
    assigned_to = QuerySelectField('Assign to User', query_factory=lambda: User.query.all(),
                                   get_label='username', allow_blank=True, blank_text='-- Assign to User --',
                                   validators=[Optional()])
    submit = SubmitField('Update Task')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Submit')

from wtforms.validators import URL, ValidationError # Import URL and ValidationError
# Ensure date is imported, and BooleanField
from datetime import date
from wtforms import BooleanField

# Custom validator for ProcessDocumentForm
def content_or_link_required(form, field):
    if not form.content.data and not form.link.data:
        raise ValidationError('Either Content or a Link to an external document is required.')
    if form.content.data and form.link.data:
        raise ValidationError('Please provide either Content or a Link, not both.')

class ProcessDocumentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Content (if not providing a link)', validators=[Optional()])
    link = StringField('Or Link to External Document (URL)', validators=[Optional(), URL()])
    category = QuerySelectField('Category', 
                                query_factory=lambda: Category.query.all(), 
                                get_label='name', allow_blank=True, blank_text='-- Select Category --',
                                validators=[Optional()])
    submit = SubmitField('Save Document')

    # Apply the custom validator to the form globally or one of the fields.
    # Attaching to 'content' field, but it checks both.
    def validate_content(self, field):
        content_or_link_required(self, field)
