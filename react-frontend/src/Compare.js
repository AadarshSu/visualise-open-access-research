import React from 'react';
import { useLocation } from "react-router-dom";
import InstitutionSelect from './InstitutionSelect';
import './App.css'

function Compare(){
    const [isLoading, setIsLoading] = React.useState(false);
    const [searchQuery, setSearchQuery] = React.useState("");
    const [searchComplete, setSearchComplete] = React.useState(false);
    const [comparisonData, setComparisonData] = React.useState(null);
    const [comparisonBreakdownData, setComparisonBreakdownData] = React.useState(null);
    const location = useLocation();
    const leftData = location.state.data;
    const leftInstitutionName = leftData.name;

    const rightImageRef = React.useRef(null);
    const rightImageRef2 = React.useRef(null);

    React.useEffect(() => {
        const fetchLeftData = async (divID, endpoint, localStorageKey, pieChartName) => {
            const imageContainer = document.getElementById(divID);
            if(!imageContainer.hasChildNodes()){
                let pie_chart;
                let data;
                // get the image from local storage
                let searchResults = localStorage.getItem(localStorageKey)
                if (searchResults){
                    searchResults = JSON.parse(searchResults);
                    pie_chart = searchResults[pieChartName];
                } else {
                    try {
                        const response = await fetch(endpoint + '?institution=' + encodeURIComponent(leftInstitutionName) + '&timeframe=' + encodeURIComponent(leftData.timeframe));
                        if (!response.ok) {
                            console.error('An error occurred:', response.statusText);
                            return;
                        }
                        data = await response.json();
                        pie_chart = data[pieChartName];
                    } catch (error) {
                        console.log("Error fetching data:", error);
                    }
                }
                if (pie_chart){
                    imageContainer.innerHTML = '';
                    const image = document.createElement('img');
                    image.src = `data:image/png;base64,${pie_chart}`;
                    imageContainer.appendChild(image);

                    // Add the data to local storage if it's not already there
                    if (!localStorage.getItem(localStorageKey)){
                        localStorage.setItem(localStorageKey, JSON.stringify(data));
                    }
                }
            }
        };
        setIsLoading(true);
        fetchLeftData('left-image', '/institution', 'searchResults', 'pie_chart');
        fetchLeftData('left-image-2', '/institution/oa_breakdown', leftInstitutionName + '_breakdown', 'detailed_pie_chart');
        setIsLoading(false);

    }, []);

    React.useEffect(() => {
        if (searchComplete && comparisonData && comparisonBreakdownData) {
            const image = document.createElement('img');
            const image2 = document.createElement('img');
            image.src = `data:image/png;base64,${comparisonData.pie_chart}`;
            image2.src = `data:image/png;base64,${comparisonBreakdownData.detailed_pie_chart}`;
            rightImageRef.current.appendChild(image);
            rightImageRef2.current.appendChild(image2);
        }
    }, [searchComplete, comparisonData, comparisonBreakdownData]);

    const handleSearchChange = (event) => {
        setSearchQuery(event.target.value);
    };

    const handleSearch = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/institution?institution=' + encodeURIComponent(searchQuery) + '&timeframe=' + encodeURIComponent(leftData.timeframe));
            const breakdownResponse = await fetch('/institution/oa_breakdown?institution=' + encodeURIComponent(searchQuery) + '&timeframe=' + encodeURIComponent(leftData.timeframe));

            if(!response.ok || !breakdownResponse.ok) {
                alert('Error: Invalid input. Please check your ORCID ID or institution name and try again.')
                // throw new Error("An error occurred");
                return;
              }
            const data = await response.json();
            const breakdownData = await breakdownResponse.json();

            setComparisonData(data);
            setComparisonBreakdownData(breakdownData);

            // if the search is successful, set the search complete flag to true
            setSearchComplete(true);

        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="page-container">
            {isLoading &&
                <div className="loading-overlay">
                <div className="loading-box">Loading...</div>
                </div>}
            <button className="back-button" onClick={()=> window.history.back()}>Back</button>
            <div className="compare-header">
                <h1>Compare Open Access Between Two Institutions for Timeframe: {leftData.timeframe}</h1>
            </div>
            <div className="compare-page-container">
                <div className='left-container'>
                    <h2 className="container-header">{leftInstitutionName}</h2>
                    <div className="image-container" id="left-image"></div>
                    <div className="image-container" id="left-image-2"></div>
                </div>
                <div className='right-container'>
                    {!searchComplete && (
                        <h2 className="container-header">Search for an institution to compare</h2>
                    )}
                    {!searchComplete && (
                        <div className="search-section">
                            <InstitutionSelect handleInstitutionChange={(seletedOption) => setSearchQuery(seletedOption.value)}/>
                            <button className="search-button" onClick={handleSearch}>Search</button>
                        </div>
                    )}
                    {searchComplete && (
                        <div className='right-container-header'>
                            <h2 className="container-header">{searchQuery}</h2>
                            <button className="change-institution-button" onClick={() => { setSearchComplete(false); setSearchQuery(''); } }>Change</button>
                        </div>
                    )}
                    {searchComplete && (
                        <div className="image-container" ref={rightImageRef} id="right-image"></div>
                    )}
                    {searchComplete && (
                        <div className='image-container' ref={rightImageRef2} id='right-image-2'></div>
                    )}
                </div>
            </div>
        </div>
    );

}

export default Compare;