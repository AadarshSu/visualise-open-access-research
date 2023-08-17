import React from "react";

function InstitutionSelect({ handleInstitutionChange }) {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [institutions, setInstitutions] = React.useState([]);

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  React.useEffect(() => {
    if (searchQuery.length > 2) {
      fetch(`/search_institutions?searchQuery=${searchQuery}`)
        .then(response => response.json())
        .then(data => setInstitutions(data))
        .catch(error => console.log(error));
    }
  }, [searchQuery]);

  return (
    <div className="institution-select">
        <input 
            type="text" 
            placeholder="e.g. University of St Andrews"
            name="search-bar" 
            value={searchQuery} 
            onChange={handleSearchChange}
        />
        {searchQuery && 
            <select size="5" onChange={e => {
                handleInstitutionChange({ value: e.target.value });
                setSearchQuery(e.target.value);
                }}>
                {institutions.map((inst, index) => (
                    <option key={index} value={inst}>
                        {inst}
                    </option>
                ))}
            </select>
        }
    </div>
);
}

export default InstitutionSelect;