import React from "react";
import { useLocation } from "react-router-dom";
import "./App.css";

function OaBreakdown() {
    const location = useLocation();
    const data = location.state.breakdownData;
    return (
      <div className="results-container">
        <button className="back-button" onClick={()=> window.history.back()}>Back</button>
        <h1>Open Access Breakdown</h1>
        <div className="image-container">
            <img src={`data:image/png;base64,${data.detailed_pie_chart}`} alt="Detailed pie chart" />
        </div>
        <h2>What does this mean?</h2>
        <table>
            <thead>
                <tr>
                    <th>OA Status</th>
                    <th>Definition</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Green</td>
                    <td>Green articles are published in toll-access journals, but archived in an OA archive, or "repository". These repositories may be discipline-specific (like ArXiv) or institutional repositories operated by universities or other institutions. Green articles may be published versions or preprints, and can have any license or no license.</td>
                </tr>
                <tr>
                    <td>Bronze</td>
                    <td>Bronze articles are free to read on the publisher's website, without a license that grants any other rights. There may be a delay between publication and availability to read, and often articles can be removed unilaterally by the publisher.</td>
                </tr>
                <tr>
                    <td>Hybrid</td>
                    <td>Hybrid articles are free to read at the time of publication, with an open license. These are usually published in exchange for an article processing charge, or APC.</td>
                </tr>
                <tr>
                    <td>Gold</td>
                    <td>Gold articles have all the same characteristics as Hybrid articles, but are published in all-Open Access journals, which are in turn called "Gold journals", or just "OA journals".</td>
                </tr>
            </tbody>
        </table>
      </div>
    );
  }
  
  export default OaBreakdown;
  