import React from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";

function Results({ data }) {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = React.useState(false);
    const [userEmail, setUserEmail] = React.useState("");

    // query the backend for the breakdown data
    const handleBreakdown = async () => {
        setIsLoading(true);
        const start = new Date();
        try{
            const breakdownKey = data.name + "_breakdown";
            // Check if we already have the breakdown data in the cache
            if (localStorage.getItem(breakdownKey)) {
                // Navigate to the breakdown page
                navigate("/oa_breakdown", { state: { breakdownData: JSON.parse(localStorage.getItem(breakdownKey)) } });
            } else {
                // check if data name is ORCID ID or institution name
                let isOrcid = false;
                if (data.name.includes("-") && data.name.length == 19){
                    isOrcid = true;
                }

                let endpoint = '';
                if (isOrcid){
                    endpoint = '/orcid/oa_breakdown?orcid=' + encodeURIComponent(data.name) + '&timeframe=' + encodeURIComponent(data.timeframe);
                } else {
                    if (data.api_key !== undefined && data.api_secret !== undefined) {
                        endpoint = '/institution/oa_breakdown?institution=' + encodeURIComponent(data.name) + '&timeframe=' + encodeURIComponent(data.timeframe) + '&api_key=' + encodeURIComponent(data.api_key) + '&api_secret=' + encodeURIComponent(data.api_secret);
                    } else {
                        endpoint = '/institution/oa_breakdown?institution=' + encodeURIComponent(data.name) + '&timeframe=' + encodeURIComponent(data.timeframe);
                    }
                }
                console.log(data.api_key);
                console.log(data.api_secret);
                console.log("fetched endpoint: " + endpoint);
                const response = await fetch(endpoint);

                if (!response.ok) {
                    console.error('An error occurred:', response.statusText);
                    return;
                }
                const breakdownData = await response.json();

                // Add the data to local storage
                localStorage.setItem(breakdownKey, JSON.stringify(breakdownData));
            
                navigate("/oa_breakdown", { state: { breakdownData } });
            }
        } finally {
            setIsLoading(false);
            const end = new Date();
            console.log("Time to load breakdown data: " + (end - start) + "ms");
        }

    };

    const handleLanguageDetails = async () => {
        setIsLoading(true);
        const start = new Date();
        try{
            const languageKey = data.name + "_language";
            // Check if we already have the breakdown data in the cache
            if (localStorage.getItem(languageKey)) {
                // Navigate to the breakdown page
                navigate("/language_details", { state: { languageData: JSON.parse(localStorage.getItem(languageKey)) } });
            } else {
                // check if data name is ORCID ID or institution name
                let isOrcid = false;
                if (data.name.includes("-") && data.name.length == 19){
                    isOrcid = true;
                }

                let endpoint = '';
                if (isOrcid){
                    endpoint = '/orcid/wiki_lang_split?orcid=' + encodeURIComponent(data.name) + '&timeframe=' + encodeURIComponent(data.timeframe);
                } else {
                    if (data.api_key !== undefined && data.api_secret !== undefined) {
                        endpoint = '/institution/wiki_lang_split?institution=' + encodeURIComponent(data.name) + '&timeframe=' + encodeURIComponent(data.timeframe)  + '&api_key=' + encodeURIComponent(data.api_key) + '&api_secret=' + encodeURIComponent(data.api_secret);
                    } else {
                        endpoint = '/institution/wiki_lang_split?institution=' + encodeURIComponent(data.name) + '&timeframe=' + encodeURIComponent(data.timeframe);
                    }
                    
                }
                const response = await fetch(endpoint);

                if (!response.ok) {
                    console.error('An error occurred:', response.statusText);
                    return;
                }
                const languageData = await response.json();

                // Add the data to local storage
                localStorage.setItem(languageKey, JSON.stringify(languageData));
            
                navigate("/language_details", { state: { languageData } });
            }
        } finally {
            setIsLoading(false);
            const end = new Date();
            console.log("Time to load language data: " + (end - start) + "ms");
        }
    };

    const handleLanguageSearch = async () => {
        setIsLoading(true);
        try{
            // navigate to the language search page and pass institution/ORCID ID as a query parameter
            navigate("/search_language", { state: { query: data.name } });
        } finally {
            setIsLoading(false);
        }
    };

    const handleComparison = async () => {
        setIsLoading(true);
        try {
            navigate("/compare", { state: { data } });
        } finally { 
            setIsLoading(false);
        }
    };

    // create button under image called "Download Citation URLs" that downloads a csv file with the URLs
    const handleCSVDownload = async () => {
        setIsLoading(true);
        try {
            // call endpoint which downloads csv file
            const response = await fetch("/institution/download_citations?institution=" + encodeURIComponent(data.name) + "&timeframe=" + encodeURIComponent(data.timeframe));
            if (!response.ok) {
                console.error('An error occurred:', response.statusText);
                return;
            }
            console.log("Downloaded CSV file");

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.name + ' Citations For ' + data.timeframe +'.csv';

            a.click();

            window.URL.revokeObjectURL(url);

        } finally {
            setIsLoading(false);
        }
    };

    const handleEmailChange = (event) => {
        setUserEmail(event.target.value);
    };

    return (
        <div className="results-container">
            {isLoading && 
                <div className="loading-overlay">
                    <div className="loading-box">Loading...</div>
                </div>}
            <h2>Wikipedia Research Citation Statistics for '{data.name}' for Timeframe: {data.timeframe}</h2>
            <div className="image-container">
                <img src={`data:image/png;base64,${data.pie_chart}`} alt="Pie chart" />
            </div>
            {/* button for download under image container */}
            <button className="download-button" onClick={handleCSVDownload}>Download Citation List</button>
            <br></br>
            <div className="email-container">
                <input
                    type="email"
                    placeholder="Enter Email Address for Monthly Reports"
                    className="search-bar"
                    value={userEmail}
                    onChange={handleEmailChange}
                />
                <button className="email-button" onClick={handleEmailChange}>Submit</button>
            </div>
            <div className="sidebar">
                <button className="back-to-home-button" onClick={()=> window.history.back()}>Back to Search</button>
                <br></br>
                <button className="details-button" onClick={handleBreakdown}>See Breakdown</button>
                <button className="language-details-button" onClick={handleLanguageDetails}>See Wikipedia Site/Language Breakdown</button>
                <button className="compare-button" onClick={handleComparison}>Create Comparison</button>
            </div>
        </div>
    );
}

export default Results;