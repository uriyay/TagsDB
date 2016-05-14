from flask import Flask
from flask import render_template, flash, redirect, request
from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

import tags_db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

db = tags_db.TagsDatabase(config.db_path)

class FactForm(Form):
    fact = StringField('fact', validators=[DataRequired()])

class SearchForm(Form):
    query = StringField('query', validators=[])

def fact_to_string(fact):
    return '%s -> %s' % (fact.text, ';'.join(fact.tags))

@app.route('/add_fact', methods=['GET', 'POST'])
def add_fact():
    form = FactForm()
    if form.validate_on_submit():
        fact = tags_db.Fact(form.fact.data)
        flash(fact_to_string(fact))
        db.add_fact(fact)
    return render_template('fact_form.html',
                           title='Add Fact',
                           form=form)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        if query != '':
            result = db.search(query)
            results_facts = [fact_to_string(x) for x in result.keys()]
        else:
            results_facts = [fact_to_string(x) for x in db.facts]
        return render_template('search_results.html',
                               title='Search',
                               results=results_facts)
    return render_template('search_form.html',
                           title='Search',
                           form=form)

@app.route('/index.html')
@app.route('/')
def home():
    return render_template('index.html',
                           title='TagsDB - tagged facts database')

if __name__ == "__main__":
    app.run(debug=True,
            host='0.0.0.0')
