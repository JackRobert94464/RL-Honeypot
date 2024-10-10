from flask import Flask, render_template, request, redirect, url_for
from autoenvgenerator import generate_tpg

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cve_file = request.form['cve_file']
        epss_file = request.form['epss_file']
        ntpg_file = request.form['ntpg_file']
        htpg_file = request.form['htpg_file']
        min_nodes = int(request.form['min_nodes'])
        max_nodes = int(request.form['max_nodes'])
        min_cves = int(request.form['min_cves'])
        max_cves = int(request.form['max_cves'])

        generate_tpg(cve_file, epss_file, ntpg_file, htpg_file, min_nodes, max_nodes, min_cves, max_cves)
        return redirect(url_for('success'))

    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)