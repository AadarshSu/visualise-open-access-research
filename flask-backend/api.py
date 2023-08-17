from flask import Flask, request, jsonify, make_response
import sqlite3
# from flask_sqlalchemy import SQLAlchemy
import requests

from server2 import getGridID, getDigest, getOADigest, getORCIDDigest, getOAORCIDDigest
from datavis import createOAPieChart, createOATypesPieChart, createLanguageBarGraph

app = Flask(__name__)

DATABASE_PATH = 'mydatabase.db'

@app.route('/search_institutions')
def search_institutions():
    try:
        # Get the query parameter from the request
        query = request.args.get('searchQuery')

        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Fetch the closes 5 matching institutions
        cursor.execute("SELECT name FROM institutions WHERE name LIKE ? LIMIT 5", (f"%{query}%",))
        results = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Check if we got the results and return it
        if results:
            institutions = [result[0] for result in results]
            print(institutions)
            return jsonify(institutions)
        else:
            print("No records in the database.")
            return "No records in the database."

    except Exception as e:
        print(f"Failed to query database: {str(e)}")
        return f"Error: {str(e)}"

api_key = 'ab2ac84dad114f7cb3bb2d3094359b99'

@app.route('/orcid', methods=['GET'])
def orcid():
    orcid = request.args.get('orcid')
    # check if the ORCID is valid by checking the length and if it contains only numbers and dashes
    if len(orcid) != 19 or not orcid.replace('-', '').isdigit():
        # send not ok response
        return make_response(jsonify({'error': 'Invalid ORCID'}), 400)
    timeframe = request.args.get('timeframe')
    digest = getORCIDDigest(orcid, timeframe)
    OAdigest = getOAORCIDDigest(orcid, 'all', timeframe)

    print('orcid: ', orcid)
    print('digest: ', digest)

    # construct the URL to retrieve the total number of citations for the institution
    if timeframe != 'all':
        total_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + digest + '&filter[mention_sources][]=type:wikipedia&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + OAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
    else:
        total_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + digest + '&filter[mention_sources][]=type:wikipedia&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + OAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key
    response1 = requests.get(total_citations_url)
    response2 = requests.get(oa_all_url)

    result = {}

    if response1.status_code == 200:
        data = response1.json()
        print('total citations: ', data['meta']['response']['total-results'])
        result['total_citations'] = data['meta']['response']['total-results']
    else:
        print('Could not retrieve university data')
        result['total_citations'] = None

    if response2.status_code == 200:
        data = response2.json()
        print('total open access citations: ', data['meta']['response']['total-results'])
        result['total_oa'] = data['meta']['response']['total-results']
    else:
        print('Could not retrieve university data')
        result['total_oa'] = None

    if result['total_citations'] is not None and result['total_oa'] is not None:
        if result['total_citations'] != 0:
            result['oa_percentage'] = result['total_oa'] / result['total_citations'] * 100
        else:
            result['oa_percentage'] = 0

    pie_chart = createOAPieChart(result['total_citations'], result['total_oa'], result['oa_percentage'])
    result['pie_chart'] = pie_chart

    result['name'] = orcid
    result['timeframe'] = timeframe

    return jsonify(result)

@app.route('/institution', methods=['GET'])
def institution():
    institution = request.args.get('institution')
    # check if institution exists in database
    
    timeframe = request.args.get('timeframe')
    grid_id, institution_name = getGridID(institution)
    digest = getDigest(grid_id, timeframe)
    allOAdigest = getOADigest(grid_id, 'all', timeframe)

    print('grid: ', grid_id)
    print('digest: ', digest)

    # construct the URL to retrieve the total number of citations for the institution
    if timeframe != 'all':
        total_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + digest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
    else:
        total_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + digest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[scope]=all&key=' + api_key
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=all&key=' + api_key
    resAllCitations = requests.get(total_citations_url)

    
    resAllOA = requests.get(oa_all_url)
    result = {}

    if resAllCitations.status_code == 200:
        data = resAllCitations.json() 
        print('total citations: ', data['meta']['response']['total-results'])
        result['total_citations'] = data['meta']['response']['total-results']
    else:
        print('Could not retrieve university data')
        result['total_citations'] = None
    
    if resAllOA.status_code == 200:
        data = resAllOA.json()
        print('total open access citations: ', data['meta']['response']['total-results'])
        result['total_oa'] = data['meta']['response']['total-results']

    else:
        print('Could not retrieve university data')
        result['total_oa'] = None

    if result['total_citations'] is not None and result['total_oa'] is not None:
        if result['total_citations'] != 0:
            result['oa_percentage'] = result['total_oa'] / result['total_citations'] * 100
        else:
            result['oa_percentage'] = 0

    pie_chart = createOAPieChart(result['total_citations'], result['total_oa'], result['oa_percentage'])
    result['pie_chart'] = pie_chart

    result['name'] = institution_name
    result['timeframe'] = timeframe

    return jsonify(result)

@app.route('/institution/oa_breakdown', methods=['GET'])
def institution_oa_breakdown():
    print("clicked")
    institution = request.args.get('institution')
    timeframe = request.args.get('timeframe')
    grid_id, institution_name = getGridID(institution)

    allOAdigest = getOADigest(grid_id, 'all', timeframe)
    goldOAdigest = getOADigest(grid_id, 'gold', timeframe)
    greenOAdigest = getOADigest(grid_id, 'green', timeframe)
    bronzeOAdigest = getOADigest(grid_id, 'bronze', timeframe)
    hybridOAdigest = getOADigest(grid_id, 'hybrid', timeframe)

    if timeframe != 'all':
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_gold_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + goldOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=gold&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_green_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + greenOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=green&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_bronze_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + bronzeOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=bronze&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_hybrid_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + hybridOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=hybrid&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
    else:
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=all&key=' + api_key
        oa_gold_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + goldOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=gold&filter[scope]=all&key=' + api_key
        oa_green_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + greenOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=green&filter[scope]=all&key=' + api_key
        oa_bronze_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + bronzeOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=bronze&filter[scope]=all&key=' + api_key
        oa_hybrid_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + hybridOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=hybrid&filter[scope]=all&key=' + api_key
    
    resAllOA = requests.get(oa_all_url)
    resGold = requests.get(oa_gold_url) 
    resGreen = requests.get(oa_green_url)  
    resBronze = requests.get(oa_bronze_url) 
    resHybrid = requests.get(oa_hybrid_url)

    result = {}
    if resAllOA.status_code == 200:
        data = resAllOA.json()
        print('total open access citations: ', data['meta']['response']['total-results'])
        result['total_oa'] = data['meta']['response']['total-results']
    else:
        print('Could not retrieve university data')
        result['total_oa'] = None

    if resGold.status_code == 200:
        data = resGold.json()
        print('total gold open access citations: ', data['meta']['response']['total-results'])
        result['total_gold_oa'] = data['meta']['response']['total-results']
    else:
        result['total_gold_oa'] = None

    if resGreen.status_code == 200:
        data = resGreen.json()
        print('total green open access citations: ', data['meta']['response']['total-results'])
        result['total_green_oa'] = data['meta']['response']['total-results']
    else:
        result['total_green_oa'] = None

    if resBronze.status_code == 200:
        data = resBronze.json()
        print('total bronze open access citations: ', data['meta']['response']['total-results'])
        result['total_bronze_oa'] = data['meta']['response']['total-results']
    else:
        result['total_bronze_oa'] = None

    if resHybrid.status_code == 200:
        data = resHybrid.json()
        print('total hybrid open access citations: ', data['meta']['response']['total-results'])
        result['total_hybrid_oa'] = data['meta']['response']['total-results']
    else:
        result['total_hybrid_oa'] = None
    
    detailed_pie_chart = createOATypesPieChart(result['total_oa'], result['total_gold_oa'], result['total_green_oa'], result['total_bronze_oa'], result['total_hybrid_oa'])
    result['detailed_pie_chart'] = detailed_pie_chart

    return jsonify(result)

@app.route('/orcid/oa_breakdown', methods=['GET'])
def orcid_oa_breakdown():
    print("clicked")
    orcid = request.args.get('orcid')
    timeframe = request.args.get('timeframe')

    allOAdigest = getOAORCIDDigest(orcid, 'all', timeframe)
    goldOAdigest = getOAORCIDDigest(orcid, 'gold', timeframe)
    greenOAdigest = getOAORCIDDigest(orcid, 'green', timeframe)
    bronzeOAdigest = getOAORCIDDigest(orcid, 'bronze', timeframe)
    hybridOAdigest = getOAORCIDDigest(orcid, 'hybrid', timeframe)

    if timeframe != 'all':
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_gold_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + goldOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=gold&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_green_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + greenOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=green&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_bronze_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + bronzeOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=bronze&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
        oa_hybrid_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + hybridOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=hybrid&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key
    else:
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key
        oa_gold_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + goldOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=gold&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key
        oa_green_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + greenOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=green&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key
        oa_bronze_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + bronzeOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=bronze&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key
        oa_hybrid_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + hybridOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=hybrid&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key

    
    resAllOA = requests.get(oa_all_url)
    resGold = requests.get(oa_gold_url)
    resGreen = requests.get(oa_green_url)
    resBronze = requests.get(oa_bronze_url)
    resHybrid = requests.get(oa_hybrid_url)

    result = {}
    if resAllOA.status_code == 200:
        data = resAllOA.json()
        print('total open access citations: ', data['meta']['response']['total-results'])
        result['total_oa'] = data['meta']['response']['total-results']
    else:
        print('Could not retrieve university data')
        result['total_oa'] = None

    if resGold.status_code == 200:
        data = resGold.json()
        print('total gold open access citations: ', data['meta']['response']['total-results'])
        result['total_gold_oa'] = data['meta']['response']['total-results']
    else:
        result['total_gold_oa'] = None

    if resGreen.status_code == 200:
        data = resGreen.json()
        print('total green open access citations: ', data['meta']['response']['total-results'])
        result['total_green_oa'] = data['meta']['response']['total-results']
    else:
        result['total_green_oa'] = None

    if resBronze.status_code == 200:
        data = resBronze.json()
        print('total bronze open access citations: ', data['meta']['response']['total-results'])
        result['total_bronze_oa'] = data['meta']['response']['total-results']
    else:
        result['total_bronze_oa'] = None

    if resHybrid.status_code == 200:
        data = resHybrid.json()
        print('total hybrid open access citations: ', data['meta']['response']['total-results'])
        result['total_hybrid_oa'] = data['meta']['response']['total-results']
    else:
        result['total_hybrid_oa'] = None
    
    detailed_pie_chart = createOATypesPieChart(result['total_oa'], result['total_gold_oa'], result['total_green_oa'], result['total_bronze_oa'], result['total_hybrid_oa'])
    result['detailed_pie_chart'] = detailed_pie_chart

    return jsonify(result)

@app.route('/institution/wiki_lang_split', methods=['GET'])
def institutionLangSplit():
    print("clicked")
    institution = request.args.get('institution')
    timeframe = request.args.get('timeframe')
    grid_id, _ = getGridID(institution)
    allOAdigest = getOADigest(grid_id, 'all', timeframe)
    closedOAdigest = getOADigest(grid_id, 'closed', timeframe)

    if timeframe != 'all':
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
        oa_closed_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + closedOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=closed&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
    else:
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=all&key=' + api_key + '&page[size]=100'
        oa_closed_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + closedOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=closed&filter[scope]=all&key=' + api_key + '&page[size]=100'

    resAllOA = requests.get(oa_all_url)
    resClosedOA = requests.get(oa_closed_url)

    result = {}

    if resAllOA.status_code == 200 and resClosedOA.status_code == 200:
        data_open = resAllOA.json()
        data_closed = resClosedOA.json()
        language_bar_graph = createLanguageBarGraph(data_open, data_closed)
        result['language_bar_graph'] = language_bar_graph
    else:
        print('Could not retrieve university data 1')
    
    return jsonify(result)

@app.route('/orcid/wiki_lang_split', methods=['GET'])
def orcidLangSplit():
    print("clicked")
    orcid = request.args.get('orcid')
    timeframe = request.args.get('timeframe')
    allOAdigest = getOAORCIDDigest(orcid, 'all', timeframe)
    closedOAdigest = getOAORCIDDigest(orcid, 'closed', timeframe)

    if timeframe != 'all':
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
        oa_closed_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + closedOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=closed&filter[orcid]=' + orcid + '&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
    else:
        oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key + '&page[size]=100'
        oa_closed_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + closedOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=closed&filter[orcid]=' + orcid + '&filter[scope]=all&key=' + api_key + '&page[size]=100'
    
    resAllOA = requests.get(oa_all_url)
    resClosedOA = requests.get(oa_closed_url)

    result = {}

    if resAllOA.status_code == 200 and resClosedOA.status_code == 200:
        data_open = resAllOA.json()
        data_closed = resClosedOA.json()
        language_bar_graph = createLanguageBarGraph(data_open, data_closed)
        result['language_bar_graph'] = language_bar_graph
    else:
        print('Could not retrieve university data 1')
    
    return jsonify(result)

# @app.route('/institution/specific_language_details', methods=['GET'])
# def specific_language_details():
#     print("clicked")
#     language = request.args.get('language')
#     institution = request.args.get('name')

#     grid_id, institution_name = getGridID(institution)
#     digest = getDigest(grid_id)
#     allOAdigest = getOADigest(grid_id, 'all')

#     # construct the URL to retrieve the total number of citations for the institution
#     total_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + digest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[scope]=all&key=' + api_key
#     resAllCitations = requests.get(total_citations_url)

#     oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=all&key=' + api_key + '&page[size]=100'
#     resAllOA = requests.get(oa_all_url)

#     result = {}

#     if resAllCitations.status_code == 200:
#         data = resAllCitations.json() 
#         print('total citations: ', data['meta']['response']['total-results'])
#         result['total_citations'] = data['meta']['response']['total-results']
#     else:
#         print('Could not retrieve university data')
#         result['total_citations'] = None
    
#     if resAllOA.status_code == 200:
#         data = resAllOA.json()
#         print('total open access citations: ', data['meta']['response']['total-results'])
#         result['total_oa'] = data['meta']['response']['total-results']
#     else:
#         print('Could not retrieve university data')
#         result['total_oa'] = None

#     if result['total_citations'] and result['total_oa'] is not None:
#         result['oa_percentage'] = result['total_oa'] / result['total_citations'] * 100

#     pie_chart = createOAPieChart(result['total_citations'], result['total_oa'], result['oa_percentage'])
#     result['pie_chart'] = pie_chart

#     return jsonify(result)

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)