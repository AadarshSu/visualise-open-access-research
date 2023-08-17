import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import './App.css'

function LanguageSearch() {
    const [isLoading, setIsLoading] = React.useState(false);
    const [searchQuery, setSearchQuery] = React.useState("");
    const navigate = useNavigate();
    const location = useLocation();
    const name = location.state.query;

    const handleSearchChange = (event) => {
        setSearchQuery(event.target.value);
    };

    const handleSearch = async () => {
        setIsLoading(true);
        const start = new Date();
        try {
            const languageKey = searchQuery + "_site";
            if(localStorage.getItem(languageKey)) {
                navigate("/language_results", { state: { languageData: JSON.parse(localStorage.getItem(languageKey)) } });
            } else {
                const response = await fetch('/institution/specific_language_details?language=' + encodeURIComponent(searchQuery) + '&name=' + encodeURIComponent(name));

                if (!response.ok) {
                    console.error('An error occurred:', response.statusText);
                    return;
                }
                const languageData = await response.json();
                // Add the data to local storage
                localStorage.setItem(languageKey, JSON.stringify(languageData));

                navigate("/language_results", { state: { languageData } });
            }
            
        } finally {
            setIsLoading(false);
            const end = new Date();
            console.log("Time to load breakdown data: " + (end - start) + "ms");
        }
    };

    return (
        <div className="page-container">
            {isLoading && 
                <div className="loading-overlay">
                <div className="loading-box">Loading...</div>
                </div>}
            <div className="header-section">
                <h1>Visualise Open Access for Specific Wikipedia Sites</h1>
            </div>
            <div className="search-section">
                <input
                type="text"
                placeholder="e.g. English, Spanish, Vietnamese"
                name="search-bar"
                className="search-bar"
                value={searchQuery}
                onChange={handleSearchChange}
                />
                <button className="search-button" onClick={handleSearch}>Search</button>
            </div>
        </div>
    );
}

export default LanguageSearch;