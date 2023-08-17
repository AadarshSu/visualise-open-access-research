import React from "react";
import { useLocation } from "react-router-dom";
import "./App.css";

function LanguageDetails() {
    const location = useLocation();
    const data = location.state.languageData;
    return (
      <div className="results-container">
        <button className="back-button" onClick={()=> window.history.back()}>Back</button>
        <h1>Wikipedia Language Split on Citations</h1>
        <div className="image-container">
            <img src={`data:image/png;base64,${data.language_bar_graph}`} alt="Language bar graph" />
        </div>
      </div>
    );
  }
  
  export default LanguageDetails;
  