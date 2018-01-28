from flask import Flask, render_template, request
from wtforms import Form, StringField, SelectField
from wtforms.validators import InputRequired, ValidationError

METRIC_CHOICES = [('levenshtein', 'Levenshtein Distance'),
                  ('jaccard', 'Jaccard Index'),
                  ('hamming', 'Hamming Distance')]

app = Flask(__name__)


# Let WTForms handle the request form
class HomeForm(Form):
    string_1 = StringField('String 1', validators=[InputRequired()], render_kw={"placeholder": "String 1"})
    string_2 = StringField('String 2', validators=[InputRequired()], render_kw={"placeholder": "String 2"})

    metric = SelectField('Choose your metric', validators=[InputRequired()], choices=METRIC_CHOICES)

    # Check that strings are the same length when running hamming distance
    def validate_metric(self, field):
        if field.data == 'hamming' and (len(self.data['string_1']) != len(self.data['string_2'])):
            raise ValidationError('String 1 & String 2 must be the same length to run the Hamming Distance metric.')


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Handles all HTTP Requests for this site, and serves as the home page.
    """
    errors = []
    form = HomeForm(request.form)

    if request.method=="POST" and form.validate():
        metric = form['metric'].data
        string_1 = form['string_1'].data
        string_2 = form['string_2'].data

        try:  # Shouldn't fail, buuut...
            result, extra_data = globals().get(metric)(string_1, string_2)
        except Exception, e:
            errors.append('Something went wrong. Try again.' + str(e))

        context ={
            'metric': metric,
            'string_1': string_1,
            'string_2': string_2,
            'result': result,
        }
        if not errors:
            return render_template('home.html', extra_data=extra_data, verbose_metrics=dict(METRIC_CHOICES), form=form, **context)

    return render_template('home.html', form=form, errors=errors)


def levenshtein(s1, s2):
    """
    Computes Levenshtein Distance for two strings via iterative method.
    Returns LD and a list of lists that can be used for visualization.
    Assumes cost = 1 for insertion, deletion, and substitution
    Implementation modified and adapted from:
    https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_full_matrix
    """
    rows = len(s2) + 1
    cols = len(s1) + 1
    dist = [[0 for x in range(cols)] for x in range(rows)]

    for i in range(1, rows):
        dist[i][0] = i
    for i in range(1, cols):
        dist[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            if s2[row - 1] == s1[col - 1]:
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row - 1][col] + 1,
                                 dist[row][col - 1] + 1,
                                 dist[row - 1][col - 1] + cost)

    return dist[row][col], {'batches': dist}


def jaccard(s1, s2):
    """
    Finds Jaccard Index based on the `intersection`/`union` definition.
    Returns the Jaccard Index as well as the set intersection & union (used in visualization).
    """
    # Find similar (distinct) elements (1)
    set_s1, set_s2 = set(s1), set(s2)
    set_intersection = set_s1.intersection(set_s2)

    # Count total distinct elements (2)
    set_union = set_s1.union(set_s2)

    # Divide (1)/(2) (and keep this fix to 3 decimal points)
    jac_index = round(float(len(set_intersection))/float(len(set_union)), 3)

    return jac_index, {'set_intersection':(', '.join(set_intersection), len(set_intersection)),
                       'set_union':(', '.join(set_union),len(set_union))}


def hamming(s1, s2):
    """
    Find Hamming Distance (# of unequal chars) for two equal-length strings.
    Returns HD and the indices of the unequal chars for visualization.
    """
    # WTForms validation should stop this from happening, but just in case...
    if len(s1) != len(s2):
        raise Exception('String lengths are unequal.')
    unmatched_indices = []  # keep track of this for visualization
    count = 0
    char_zip = zip(s1, s2)
    for i in range(len(char_zip)):
        if char_zip[i][0] != char_zip[i][1]:
            count += 1
            unmatched_indices.append(i)
    return count, {'unmatched_indices': unmatched_indices}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # Linux OS
    # app.run()  # Win OS
