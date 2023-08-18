import matplotlib
import requests
import urllib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from collections import Counter
from urllib.parse import urlparse

def createOAPieChart(total_citations, total_oa, oa_percentage):
    # check if total_oa is 0
    if total_citations == 0:
        # All values are zero, create a figure with a text
        fig, ax = plt.subplots()
        text = 'There are no citations tied to this person/institution.'
        ax.text(0.5, 0.5, text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off') # Hide the x and y axes
        
        # save figure into BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # encode the image into base64 and decode it into a string
        image_base64 = base64.b64encode(buf.read()).decode()

        # close the figure to free up memory
        plt.close()

        return image_base64


    # create the pie chart that shows the percentage of open access citations
    labels = ['Open Access', 'Closed Access']
    values = [oa_percentage, 100 - oa_percentage]
    colors = ['#00cc00', 'red']
    hatches = ['//', '*']
    data = [total_oa, total_citations - total_oa]
    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # pie chart
    wedges, _, autotexts = ax1.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_bbox(dict(facecolor='black', alpha=0.6, edgecolor='w', boxstyle="round,pad=0.5"))

    for i, wedge in enumerate(wedges):
        wedge.set_hatch(hatches[i])

    ax1.axis('equal')
    ax1.set_title('Percentage of Open Access Citations on Wikipedia')

    # bar graph
    bars = ax2.bar(labels, data, color=colors)
    ax2.set_title('Number of Open and Closed Access Citations on Wikipedia')
    ax2.set_ylabel('Number of Citations')

    max_height = max(data)
    scaling_factor = max_height * 0.1

    # add the data labels to the bar graph
    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, round(yval, 2), ha='center', va='bottom')

    # Increase the y-axis range to provide space at the top
    ax2.set_ylim(top=(max_height + scaling_factor))
    
    plt.subplots_adjust(wspace=0.5)

    # save figure into BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # encode the image into base64 and decode it into a string
    image_base64 = base64.b64encode(buf.read()).decode()

    # close the figure to free up memory
    plt.close()

    return image_base64

def createOATypesPieChart(total_oa, total_gold_oa, total_green_oa, total_bronze_oa, total_hybrid_oa):
    # check if total_oa is 0
    if total_oa == 0:
        # All values are zero, create a figure with a text
        fig, ax = plt.subplots()
        text = 'There are no open access citations tied to this person/institution.'
        ax.text(0.5, 0.5, text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off') # Hide the x and y axes
        
        # save figure into BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # encode the image into base64 and decode it into a string
        image_base64 = base64.b64encode(buf.read()).decode()

        # close the figure to free up memory
        plt.close()

        return image_base64
    
    gold_oa_percentage = (total_gold_oa / total_oa) * 100
    green_oa_percentage = (total_green_oa / total_oa) * 100
    bronze_oa_percentage = (total_bronze_oa / total_oa) * 100
    hybrid_oa_percentage = (total_hybrid_oa / total_oa) * 100

    # create the pie chart that shows the percentage of open access citations
    labels = ['Gold', 'Green', 'Bronze', 'Hybrid']
    values = [gold_oa_percentage, green_oa_percentage, bronze_oa_percentage, hybrid_oa_percentage]
    colors = ['#ffcc00', '#00cc00', '#ff6666', '#ff9900']
    hatches = ['//', '*', 'x', '\\']
    data = [total_gold_oa, total_green_oa, total_bronze_oa, total_hybrid_oa]
    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # pie chart
    wedges, _, autotexts = ax1.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.7)
    # wedges, _, autotexts = ax1.pie(values, labels=labels, colors=colors, autopct=autopct_format(values), startangle=90, pctdistance=0.7)
    ax1.axis('equal')
    ax1.set_title('Open Access Citations Type Breakdown')

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_bbox(dict(facecolor='black', alpha=0.6, edgecolor='w', boxstyle="round,pad=0.5"))

    for i, wedge in enumerate(wedges):
        wedge.set_hatch(hatches[i])

    # bar graph
    bars = ax2.bar(labels, data, color=colors)
    ax2.set_title('Number of Open Access Citations by Type')
    ax2.set_ylabel('Number of Citations')

    max_height = max(data)
    scaling_factor = max_height * 0.1

    # add the data labels to the bar graph
    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, round(yval, 2), ha='center', va='bottom')

    # Increase the y-axis range to provide space at the top
    ax2.set_ylim(top=(max_height + scaling_factor))
    
    plt.subplots_adjust(wspace=0.8)

    # save figure into BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # encode the image into base64 and decode it into a string
    image_base64 = base64.b64encode(buf.read()).decode()

    # close the figure to free up memory
    plt.close()

    return image_base64

def process_data(entry, language_map):
    url = entry["attributes"]["url"]
    parsed_url = urlparse(url)
    language_code = parsed_url.netloc.split('.')[0]
    language = language_map.get(language_code, language_code)

    return language

def fetch_data(url):
    response = requests.get(url)
    data = response.json()

    return data

def createLanguageBarGraph(data_open, data_closed):
    if data_open["data"] == [] and data_closed["data"] == []:
        # All values are zero, create a figure with a text
        fig, ax = plt.subplots()
        text = 'There are no citations tied to this person/institution.'
        ax.text(0.5, 0.5, text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')

        # save figure into BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # encode the image into base64 and decode it into a string
        image_base64 = base64.b64encode(buf.read()).decode()

        # close the figure to free up memory
        plt.close()
        return image_base64

    language_map = {
        'en': 'English',
        'de': 'German',
        'fr': 'French',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'fa': 'Persian',
        'ko': 'Korean',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'pl': 'Polish',
        'cs': 'Czech',
        'fi': 'Finnish',
        'tr': 'Turkish',
        'id': 'Indonesian',
        'he': 'Hebrew',
        'hu': 'Hungarian',
        'no': 'Norwegian',
        'da': 'Danish',
        'uk': 'Ukrainian',
        'sr': 'Serbian',
        'ca': 'Catalan',
        'sk': 'Slovak',
        'vi': 'Vietnamese',
        'ro': 'Romanian',
        'hr': 'Croatian',
        'bg': 'Bulgarian',
        'sl': 'Slovenian',
        'et': 'Estonian',
        'el': 'Greek',
        'hi': 'Hindi',
        'th': 'Thai',
        'la': 'Latin',
        'ta': 'Tamil',
        'bn': 'Bengali',
    }

    languages_open = []
    languages_closed = []
    executor = ThreadPoolExecutor(max_workers=10)

    # iterate through paginated JSON response and extract the language of each citation
    while True:
        futures = [executor.submit(process_data, entry, language_map) for entry in data_open["data"]]
        for future in concurrent.futures.as_completed(futures):
            languages_open.append(future.result())

        futures = [executor.submit(process_data, entry, language_map) for entry in data_closed["data"]]
        for future in concurrent.futures.as_completed(futures):
            languages_closed.append(future.result())

        # check if 'next' key is in the response, if not break the loop
        if 'next' not in data_open["links"]:
            break
        # get the next page of the JSON response
        next_page = data_open["links"]["next"]
        next_page = urllib.parse.unquote(next_page)
        data_open = executor.submit(fetch_data, next_page).result()

        if 'next' not in data_closed["links"]:
            break
        # get the next page of the JSON response
        next_page = data_closed["links"]["next"]
        next_page = urllib.parse.unquote(next_page)
        data_closed = executor.submit(fetch_data, next_page).result()

    language_count_open = Counter(languages_open)
    language_count_closed = Counter(languages_closed)

    # get all unique languages
    all_languages = set(language_count_open.keys()).union(set(language_count_closed.keys()))

    # fill in missing languages with 0
    for language in all_languages:
        if language not in language_count_open:
            language_count_open[language] = 0
        if language not in language_count_closed:
            language_count_closed[language] = 0

    # langs, counts = zip(*language_count.items())
    langs, counts_open = zip(*language_count_open.items())
    langs, counts_closed = zip(*language_count_closed.items())

    # Combine the languages, counts_open and counts_closed into a list of tuples
    combined = list(zip(langs, counts_open, counts_closed))

    # Sort the list of tuples by counts_open and counts_closed (2nd and 3rd element) in descending order
    combined.sort(key=lambda x: x[1]+x[2], reverse=True)

    # extract the top 15 languages
    combined = combined[:15]

    # Extract the sorted languages, counts_open and counts_closed
    langs_sorted, counts_open_sorted, counts_closed_sorted = zip(*combined)

    x_coords = np.arange(len(langs_sorted))

    # create bar graph
    plt.figure(figsize=(17, 10))
    bar_width = 0.4
    bars_open = plt.bar(x_coords - bar_width/2, counts_open_sorted, width=bar_width, color='#00cc00', align='center', label='Open Access')
    bars_closed = plt.bar(x_coords + bar_width/2, counts_closed_sorted, width=bar_width, color='red', align='center', label='Closed Access')
    # plt.xlim(min(x_coords)-bar_width, max(x_coords)+bar_width)
    plt.ylim(0, max(max(counts_open_sorted), max(counts_closed_sorted)) * 1.1) # 10% padding
    plt.title('Top 15 Wikipedia Sites with the Most Citations')
    plt.xlabel('Wikipedia Site')
    plt.ylabel('Citation Count')
    plt.legend()

    plt.xticks(x_coords, langs_sorted, rotation=90)
    plt.subplots_adjust(bottom=0.2) # Adjust the bottom margin to be 20% of the figure height

    # add the data labels to the bar graph
    for bar in bars_open:
        yval = bar.get_height()
        bar.set_hatch('//')
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, round(yval, 2), ha='center', va='bottom')
    
    for bar in bars_closed:
        yval = bar.get_height()
        bar.set_hatch('*')
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, round(yval, 2), ha='center', va='bottom')

    # save figure into BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # encode the image into base64 and decode it into a string
    image_base64 = base64.b64encode(buf.read()).decode()

    # close the figure to free up memory
    plt.close()

    return image_base64

