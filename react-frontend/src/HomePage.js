import React from "react";
import { BrowserRouter as Router, Route, Routes, useNavigate } from "react-router-dom";
import "./App.css";
import Results from "./Results";
import OaBreakdown from "./OaBreakdown";
import LanguageDetails from "./LanguageDetails";
import LanguageSearch from "./LanguageSearch";
import Compare from "./Compare";
import InstitutionSelect from "./InstitutionSelect";

function SearchForm({ onSearch }) {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [searchType, setSearchType] = React.useState("institution");
  const [timeframe, setTimeframe] = React.useState("all");
  const [isLoading, setIsLoading] = React.useState(false);
  const [apiKey, setApiKey] = React.useState("");
  const [secretKey, setSecretKey] = React.useState("");
  const navigate = useNavigate();

  React.useEffect(() => {
    // Clear localStorage
    window.localStorage.clear();
  }, []);

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchTypeChange = (event) => {
    setSearchType(event.target.value);
  };

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  const handleApiKeyChange = (event) => {
    setApiKey(event.target.value);
  };

  const handleSecretKeyChange = (event) => {
    setSecretKey(event.target.value);
  };

  const handleSearch = () => {

    if (!searchQuery) {
      alert('Please fill in the required textbox (insitution name/ORCID ID).');
      return;
    }

    setIsLoading(true);

    const selectedTimeframe = timeframe || "all";

    onSearch(searchQuery, searchType, selectedTimeframe, apiKey, secretKey)
      .then(() => {
        navigate("/results");
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  return (
    <div className="main-page-container">
      {isLoading && 
        <div className="loading-overlay">
          <div className="loading-box">Loading...</div>
        </div>}
      <div className="header-section">
        <h1>Visualise your research citations on Wikipedia</h1>
      </div>
      <div className="search-section">
        <select value={searchType} onChange={handleSearchTypeChange} className="search-select">
          <option value="institution">Institution</option>
          <option value="orcid">ORCID ID</option>
        </select>
        {searchType === "institution" ? <InstitutionSelect handleInstitutionChange={(seletedOption) => setSearchQuery(seletedOption.value)}/>
          : <input
          type="text"
          placeholder="e.g. 0000-0002-1825-0097"
          name="search-bar"
          className="search-bar"
          value={searchQuery}
          onChange={handleSearchChange}
        />}
        
        <select value={timeframe} onChange={handleTimeframeChange} className="search-select">
          <option value="all">All time</option>
          <option value="day">Last day</option>
          <option value="3days">Last 3 days</option>
          <option value="week">Last week</option>
          <option value="month">Last month</option>
          <option value="3months">Last 3 months</option>
          <option value="6months">Last 6 months</option>
          <option value="year">Last year</option>
        </select>
      </div>
      {searchType === "institution" && (
        <div className="api-container">
            <p className="api-text">Optional: Enter Altmetric API Keys (for chosen institution) For More Accurate Results</p>
            <input
              type="password"
              placeholder="Enter Altmetric API Key"
              className="search-bar"
              value={apiKey}
              onChange={handleApiKeyChange}
            />
            
            <input
              type="password"
              placeholder="Enter Altmetric Secret Key"
              className="search-bar"
              value={secretKey}
              onChange={handleSecretKeyChange}
            />
        </div>
      )}
        <button className="search-button" onClick={() => handleSearch(searchQuery, searchType, timeframe, apiKey, secretKey)}>Search</button>
    </div>
  );
}

function App() {
  const [searchResults, setSearchResults] = React.useState([]);

  React.useEffect(() => {
    const cachedResults = localStorage.getItem("searchResults");
    if (cachedResults) {
      setSearchResults(JSON.parse(cachedResults));
    }
  }, []);

  const handleSearch = (query, type, timeframe, apiKey, secretKey) => {
    console.log("HELLO: ", query, type, timeframe, apiKey, secretKey)
    // map the timeframe to the correct format
    switch (timeframe) {
      case "all":
        timeframe = "all";
        break;
      case "day":
        timeframe = "1d";
        break;
      case "3days":
        timeframe = "3d";
        break;
      case "week":
        timeframe = "1w";
        break;
      case "month":
        timeframe = "1m";
        break;
      case "3months":
        timeframe = "3m";
        break;
      case "6months":
        timeframe = "6m";
        break;
      case "year":
        timeframe = "1y";
        break;
      default:
        timeframe = "all";
    }
    let apiUrl = `/${type}?${type}=${query}&timeframe=${timeframe}`;
    if (apiKey !== "" && secretKey !== "") {
      console.log("API keys present:", apiKey, secretKey);
      apiUrl += `&api_key=${apiKey}&api_secret=${secretKey}`;
    }
    console.log("API URL:", apiUrl)
    return fetch(apiUrl)
      .then(response => {
        if(!response.ok) {
          alert('Error: Invalid input. Please check your ORCID ID, API key, or Secret key and try again.')
          throw new Error("An error occurred");
          // return;
        }
        return response.json();
      })
      .then(data => {
        console.log(data);
        setSearchResults(data);
        localStorage.setItem("searchResults", JSON.stringify(data));
        return data;
      })
      .catch(error => {
        console.log(error);
        throw error;
      });
  };

  return (
    <Router>
      <div className="App">
        <main>
          <Routes>
            <Route path="/" element={<SearchForm onSearch={handleSearch} />} />            
            <Route path="/results" element={<Results data={searchResults} />} />
            <Route path="/oa_breakdown" element={<OaBreakdown />} /> 
            <Route path="/language_details" element={<LanguageDetails />} />
            <Route path="/search_language" element={<LanguageSearch />} />
            <Route path="/compare" element={<Compare />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
