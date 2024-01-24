from flask import Flask, request, jsonify, make_response, send_file
import sqlite3
import requests

from generateIDs import getGridID, getDigest, getOADigest, getORCIDDigest, getOAORCIDDigest
from datavis import createOAPieChart, createOATypesPieChart, createLanguageBarGraph, createURLCSV

app = Flask(__name__)

DATABASE_PATH = 'mydatabase.db'

# search for institutions in the local database
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

# default API key for Altmetric Explorer API for the University of St Andrews - allow user to submit their own API key for better data retrieval
def get_default_api_key():
    return '95b11f1ba9cf495d8dd457db8a2ee6a4'

api_key = get_default_api_key()

# function can be used to fetch the total number of citations for a given institution for the last month
# @app.route('/institution/generate_monthly_reports', methods=['GET'])
# def generate_monthly_reports():
#     print("clicked")
#     institution = request.args.get('institution')
#     timeframe = '1m'
#     api_key_provided = request.args.get('api_key')
#     secret_key_provided = request.args.get('api_secret')

#     if api_key_provided:
#         api_key = api_key_provided
#     else:
#         api_key = get_default_api_key()

#     if secret_key_provided:
#         allOAdigest = getOADigest(institution, 'all', timeframe, secret_key_provided)
#         oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
#     else:
#         grid_id, _ = getGridID(institution)
#         allCitationsDigest = getDigest(grid_id, timeframe, None)

#         all_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allCitationsDigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
        
#     resAllCitations = requests.get(all_citations_url)

#     result = {}

#     if resAllCitations.status_code == 200:
#         data_all = resAllCitations.json()
#         url_csv_file = createURLCSV(data_all)

#         # set headers to trigger file download in browser
#         response = send_file(url_csv_file, as_attachment=True, download_name='Monthly Citation Report ' + institution + ' ' + timeframe +'.csv')
        
#         return response
#     else:
#         print('Could not retrieve university data: download failed')
    
#     return jsonify(result)

# ORCID ID endpoint - less features than institution endpoint (one way to expand would be to add all institution features to ORCID endpoint)
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

# institution endpoint
@app.route('/institution', methods=['GET'])
def institution():
    print("received")
    institution = request.args.get('institution')
    timeframe = request.args.get('timeframe')
    provided_api_key = request.args.get('api_key')
    provided_secret_key = request.args.get('api_secret')
    user_provided_api_keys = False

    if provided_api_key and provided_secret_key:
        user_provided_api_keys = True
        print("user provided api keys")
    
    if provided_api_key:
        api_key = provided_api_key
    else:
        api_key = get_default_api_key()

    if provided_secret_key:
        print("yes, secret key provided")
        digest = getDigest(None, timeframe, provided_secret_key, user_provided_api_keys)
        allOAdigest = getOADigest(None, 'all', timeframe, provided_secret_key, user_provided_api_keys)
        _, institution_name = getGridID(institution)

        print('digest: ', digest)

        # construct the URL to retrieve the total number of citations for the institution
        if timeframe != 'all':
            total_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + digest + '&filter[mention_sources][]=type:wikipedia&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
            oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
        else:
            total_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + digest + '&filter[mention_sources][]=type:wikipedia&filter[scope]=institution&key=' + api_key
            oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=institution&key=' + api_key
    else:
        print("not provided")
        grid_id, institution_name = getGridID(institution)
        digest = getDigest(grid_id, timeframe, None, user_provided_api_keys)
        allOAdigest = getOADigest(grid_id, 'all', timeframe, None, user_provided_api_keys)

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
    print("total URL:", total_citations_url)
    print("OA URL:", oa_all_url)
    result = {}

    if resAllCitations.status_code == 200:
        data = resAllCitations.json() 
        print('total citations: ', data['meta']['response']['total-results'])
        result['total_citations'] = data['meta']['response']['total-results']
    else:
        print('Could not retrieve university data for all citations')
        result['total_citations'] = None
    
    if resAllOA.status_code == 200:
        data = resAllOA.json()
        print('total open access citations: ', data['meta']['response']['total-results'])
        result['total_oa'] = data['meta']['response']['total-results']
    else:
        print('Could not retrieve university data for open access citations')
        result['total_oa'] = None

    if result['total_citations'] is not None and result['total_oa'] is not None:
        if result['total_citations'] != 0:
            result['oa_percentage'] = result['total_oa'] / result['total_citations'] * 100
        else:
            result['oa_percentage'] = 0
    else:
        print('Could not retrieve university data, possibly due to invalid API/secret key')
        # send not ok response
        return make_response(jsonify({'error': 'Could not retrieve university data, possibly due to invalid API/secret key'}), 400)

    pie_chart = createOAPieChart(result['total_citations'], result['total_oa'], result['oa_percentage'])
    result['pie_chart'] = pie_chart

    result['name'] = institution_name
    result['timeframe'] = timeframe
    if user_provided_api_keys:
        result['api_key'] = api_key
        result['api_secret'] = provided_secret_key

    return jsonify(result)

# retrieve open access breakdown information (gold, green, bronze, hybrid) for a given institution
@app.route('/institution/oa_breakdown', methods=['GET'])
def institution_oa_breakdown():
    print("clicked")
    institution = request.args.get('institution')
    timeframe = request.args.get('timeframe')
    provided_api_key = request.args.get('api_key')
    provided_secret_key = request.args.get('api_secret')
    user_provided_api_keys = False

    if provided_api_key and provided_secret_key:
        user_provided_api_keys = True
        print("user provided api keys")

    if provided_api_key:
        api_key = provided_api_key
    else:
        api_key = get_default_api_key()
    
    if provided_secret_key:
        allOAdigest = getOADigest(None, 'all', timeframe, provided_secret_key, user_provided_api_keys)
        goldOAdigest = getOADigest(None, 'gold', timeframe, provided_secret_key, user_provided_api_keys)
        greenOAdigest = getOADigest(None, 'green', timeframe, provided_secret_key, user_provided_api_keys)
        bronzeOAdigest = getOADigest(None, 'bronze', timeframe, provided_secret_key, user_provided_api_keys)
        hybridOAdigest = getOADigest(None, 'hybrid', timeframe, provided_secret_key, user_provided_api_keys)

        if timeframe != 'all':
            oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
            oa_gold_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + goldOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=gold&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
            oa_green_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + greenOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=green&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
            oa_bronze_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + bronzeOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=bronze&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
            oa_hybrid_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + hybridOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=hybrid&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
        else:
            oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=institution&key=' + api_key
            oa_gold_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + goldOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=gold&filter[scope]=institution&key=' + api_key
            oa_green_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + greenOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=green&filter[scope]=institution&key=' + api_key
            oa_bronze_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + bronzeOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=bronze&filter[scope]=institution&key=' + api_key
            oa_hybrid_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + hybridOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=hybrid&filter[scope]=institution&key=' + api_key
    else:
        grid_id, _ = getGridID(institution)

        allOAdigest = getOADigest(grid_id, 'all', timeframe, None, user_provided_api_keys)
        goldOAdigest = getOADigest(grid_id, 'gold', timeframe, None, user_provided_api_keys)
        greenOAdigest = getOADigest(grid_id, 'green', timeframe, None, user_provided_api_keys)
        bronzeOAdigest = getOADigest(grid_id, 'bronze', timeframe, None, user_provided_api_keys)
        hybridOAdigest = getOADigest(grid_id, 'hybrid', timeframe, None, user_provided_api_keys)

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

# retrieve open access breakdown information (gold, green, bronze, hybrid) for a given ORCID ID
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

# retrieve data about the different language sites that have cited research from a given institution (en, de, fr, etc.)
@app.route('/institution/wiki_lang_split', methods=['GET'])
def institutionLangSplit():
    print("clicked")
    institution = request.args.get('institution')
    timeframe = request.args.get('timeframe')
    provided_api_key = request.args.get('api_key')
    provided_secret_key = request.args.get('api_secret')
    user_provided_api_keys = False

    if provided_api_key and provided_secret_key:
        user_provided_api_keys = True
        print("user provided api keys")

    if provided_api_key:
        api_key = provided_api_key
    else:
        api_key = get_default_api_key()
    
    if provided_secret_key:
        allOAdigest = getOADigest(None, 'all', timeframe, provided_secret_key, user_provided_api_keys)
        closedOAdigest = getOADigest(None, 'closed', timeframe, provided_secret_key, user_provided_api_keys)

        # construct the URL to retrieve the total number of citations for the institution
        if timeframe != 'all':
            oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
            oa_closed_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + closedOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=closed&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key
        else:
            oa_all_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=oa_all&filter[scope]=institution&key=' + api_key
            oa_closed_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + closedOAdigest + '&filter[mention_sources][]=type:wikipedia&filter[open_access_types][]=closed&filter[scope]=institution&key=' + api_key
    else:
        grid_id, _ = getGridID(institution)
        allOAdigest = getOADigest(grid_id, 'all', timeframe, None, user_provided_api_keys)
        closedOAdigest = getOADigest(grid_id, 'closed', timeframe, None, user_provided_api_keys)

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

# retrieve data about the different language sites that have cited research from a given ORCID ID (en, de, fr, etc.)
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

# retrieve data to populate CSV file for download (data about the Wikipedia page that cited the research, and the research itself)
@app.route('/institution/download_citations', methods=['GET'])
def download_citations():
    print("clicked")
    institution = request.args.get('institution')
    timeframe = request.args.get('timeframe')
    provided_api_key = request.args.get('api_key')
    provided_secret_key = request.args.get('api_secret')
    user_provided_api_keys = False

    if provided_api_key and provided_secret_key:
        user_provided_api_keys = True
        print("user provided api keys")

    if provided_api_key:
        api_key = provided_api_key
    else:
        api_key = get_default_api_key()

    if provided_secret_key:
        # allOAdigest = getOADigest(None, 'all', timeframe, provided_secret_key, user_provided_api_keys)
        allCitationsDigest = getDigest(None, timeframe, provided_secret_key, user_provided_api_keys)

        if timeframe != 'all':
            all_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allCitationsDigest + '&filter[mention_sources][]=type:wikipedia&filter[scope]=institution&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
        else:
            all_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allCitationsDigest + '&filter[mention_sources][]=type:wikipedia&filter[scope]=institution&key=' + api_key + '&page[size]=100'
    else:
        grid_id, _ = getGridID(institution)
        allCitationsDigest = getDigest(grid_id, timeframe, None, user_provided_api_keys)

        if timeframe != 'all':
            all_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allCitationsDigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[scope]=all&filter[timeframe]=' + timeframe + '&key=' + api_key + '&page[size]=100'
        else:
            all_citations_url = 'https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=' + allCitationsDigest + '&filter[affiliations][]=' + grid_id + '&filter[mention_sources][]=type:wikipedia&filter[scope]=all&key=' + api_key + '&page[size]=100'

    resAllCitations = requests.get(all_citations_url)

    result = {}

    if resAllCitations.status_code == 200:
        data_all = resAllCitations.json()
        url_csv_file = createURLCSV(data_all)

        # set headers to trigger file download in browser
        response = send_file(url_csv_file, as_attachment=True, download_name='All Citations_' + institution + '_' + timeframe +'.csv')
        
        return response
    else:
        print('Could not retrieve university data: download failed')
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)