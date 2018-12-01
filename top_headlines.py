from flask import Flask, render_template
import requests
import json
from datetime import datetime
from secrets_example import api_key

app = Flask(__name__)
CACHE_FILE = "nyttechcache.json"
MAX_STALENESS = 10000


@app.route('/')
def welcome():
    return render_template('welcome.html')


try:
    open_cache_nyt = open(CACHE_FILE, 'r')
    read_cache_nyt = open_cache_nyt.read()
    nyt_CACHE_DICTION = json.loads(read_cache_nyt)
    open_cache_nyt.close()
except Exception as e:
    nyt_CACHE_DICTION = {}
    print(e)


def is_fresh(cache_entry):
    now = datetime.now().timestamp()
    staleness = now - cache_entry['cache_timestamp']
    return staleness < MAX_STALENESS


def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)


def get_nyt_request(section):
    baseurl = "https://api.nytimes.com/svc/topstories/v2/"
    baseurl_nyt = baseurl + section + ".json"
    params_d_nyt = {'api_key': api_key}
    unq_id = params_unique_combination(baseurl_nyt, params_d_nyt)
    if unq_id in nyt_CACHE_DICTION:
        if is_fresh(nyt_CACHE_DICTION[unq_id]):
            print("Getting data from nyt cache")
            return nyt_CACHE_DICTION[unq_id]
        else:
            print("Getting request from nyt API")
            request_nyt = requests.get(baseurl_nyt, params=params_d_nyt)
            requested_nyt_diction = json.loads(request_nyt.text)
            nyt_CACHE_DICTION[unq_id] = requested_nyt_diction
            nyt_CACHE_DICTION[unq_id]['cache_timestamp'] = datetime.now().timestamp()
            open_cache_nyt2 = open(CACHE_FILE, 'w')
            create_dump_nyt = json.dumps(nyt_CACHE_DICTION)
            open_cache_nyt2.write(create_dump_nyt)
            open_cache_nyt2.close()
            return nyt_CACHE_DICTION[unq_id]
    else:
        print("Getting request from nyt API")
        request_nyt = requests.get(baseurl_nyt, params=params_d_nyt)
        requested_nyt_diction = json.loads(request_nyt.text)
        nyt_CACHE_DICTION[unq_id] = requested_nyt_diction
        nyt_CACHE_DICTION[unq_id]['cache_timestamp'] = datetime.now().timestamp()
        open_cache_nyt2 = open(CACHE_FILE, 'w')
        create_dump_nyt = json.dumps(nyt_CACHE_DICTION)
        open_cache_nyt2.write(create_dump_nyt)
        open_cache_nyt2.close()
        return nyt_CACHE_DICTION[unq_id]


@app.route('/user/<name>')
def hello_name(name, section="technology"):
    lowercase_section = section.lower()
    first_letter = lowercase_section[0].upper()
    rest_of_section = lowercase_section[1:]
    search_param_section = first_letter + rest_of_section
    articles = {}
    response = get_nyt_request(lowercase_section)
    print(response)
    count = 0
    for each_article in response["results"]:
        if each_article["section"] == search_param_section:
            title = each_article["title"]
            url = each_article["url"]
            articles[title] = url
            count += 1
            if count == 5:
                break
    return render_template('user.html', name=name, section=section, articles=articles)


if __name__ == '__main__':
    print('starting Flask app', app.name)
    app.run(debug=True)

