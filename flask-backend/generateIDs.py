import requests
import hmac
import hashlib
import urllib.parse

# API secret for the Altmetric Explorer API for the University of St Andrews
def get_default_secret_key():
    return '9f14dee258d440679acc27690e0fa7d2'
api_secret = get_default_secret_key()

# retrieves the GRID ID of the institution from the Registry of Research (ROR) API
def getGridID(institution):
    encoded_institution = urllib.parse.quote('"' + institution + '"')
    url = 'https://api.ror.org/organizations?query=' + encoded_institution
    response = requests.get(url)
    
    # get the GRID ID of the first result
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            # return GRID ID of first result and the name of the institution
            return data['items'][0]['external_ids']['GRID']['preferred'], data['items'][0]['name']
    else:
        print('Could not retrieve GRID ID')
        return None
    
# constructs the digest for the API call - required by the Altmetric Explorer API
def getDigest(grid_id, timeframe, secret_key_provided, user_provided_api_keys):
    if user_provided_api_keys:
        api_secret = secret_key_provided
        if timeframe != 'all':
            # if user provides an API secret key, search Altmetric Explorer API using "institution" scope
            filters = 'mention_sources|type:wikipedia|scope|institution|timeframe|' + timeframe
        else:
            filters = 'mention_sources|type:wikipedia|scope|institution'
    else:
        api_secret = get_default_secret_key()
        if timeframe != 'all':
            filters = 'affiliations|' + grid_id + '|mention_sources|type:wikipedia|scope|all|timeframe|' + timeframe
        else:
            filters = 'affiliations|' + grid_id + '|mention_sources|type:wikipedia|scope|all'
    
    hmac_digest = hmac.new(api_secret.encode(), filters.encode(), hashlib.sha1)
    
    digest = hmac_digest.hexdigest()

    return digest

def getOADigest(grid_id, oa_type, timeframe, secret_key_provided, user_provided_api_keys):
    if user_provided_api_keys:
        api_secret = secret_key_provided
        base_filters = 'mention_sources|type:wikipedia|open_access_types|'
        scope_filter = '|scope|institution'
        if oa_type == 'all':
            filters = base_filters + 'oa_all' + scope_filter
        elif oa_type == 'gold':
            filters = base_filters + 'gold' + scope_filter
        elif oa_type == 'green':
            filters = base_filters + 'green' + scope_filter
        elif oa_type == 'bronze':
            filters = base_filters + 'bronze' + scope_filter
        elif oa_type == 'hybrid':
            filters = base_filters + 'hybrid' + scope_filter
        elif oa_type == 'closed':
            filters = base_filters + 'closed' + scope_filter

        if timeframe != 'all':
            filters += '|timeframe|' + timeframe
    else:
        api_secret = get_default_secret_key()
        base_filters = 'affiliations|' + grid_id + '|mention_sources|type:wikipedia|open_access_types|'
        scope_filter = '|scope|all'
        if oa_type == 'all':
            filters = base_filters + 'oa_all' + scope_filter
        elif oa_type == 'gold':
            filters = base_filters + 'gold' + scope_filter
        elif oa_type == 'green':
            filters = base_filters + 'green' + scope_filter
        elif oa_type == 'bronze':
            filters = base_filters + 'bronze' + scope_filter
        elif oa_type == 'hybrid':
            filters = base_filters + 'hybrid' + scope_filter
        elif oa_type == 'closed':
            filters = base_filters + 'closed' + scope_filter

        if timeframe != 'all':
            filters += '|timeframe|' + timeframe
            
    # print("THESE ARE THE FILTERS:", filters)
    hmac_digest = hmac.new(api_secret.encode(), filters.encode(), hashlib.sha1)
    
    digest = hmac_digest.hexdigest()

    return digest

def getORCIDDigest(orcid, timeframe):
    if timeframe != 'all':
        filters = 'mention_sources|type:wikipedia|orcid|' + orcid + '|scope|all|timeframe|' + timeframe
    else:
        filters = 'mention_sources|type:wikipedia|orcid|' + orcid + '|scope|all'
    hmac_digest = hmac.new(api_secret.encode(), filters.encode(), hashlib.sha1)
    digest = hmac_digest.hexdigest()
    return digest

def getOAORCIDDigest(orcid, type, timeframe):
    base_filters = 'mention_sources|type:wikipedia|open_access_types|'
    scope_filter = '|orcid|' + orcid + '|scope|all'
    if type == 'all':
        filters = base_filters + 'oa_all' + scope_filter
    elif type == 'gold':
        filters = base_filters + 'gold' + scope_filter
    elif type == 'green':
        filters = base_filters + 'green' + scope_filter
    elif type == 'bronze':
        filters = base_filters + 'bronze' + scope_filter
    elif type == 'hybrid':
        filters = base_filters + 'hybrid' + scope_filter
    elif type == 'closed':
        filters = base_filters + 'closed' + scope_filter

    if timeframe != 'all':
        filters += '|timeframe|' + timeframe

    hmac_digest = hmac.new(api_secret.encode(), filters.encode(), hashlib.sha1)
    digest = hmac_digest.hexdigest()
    return digest