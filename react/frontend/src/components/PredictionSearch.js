import React, { useState } from 'react';
import './PredictionSearch.css';

const PredictionSearch = ({ predictions, setFilteredPredictions }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e) => {
    const term = e.target.value;
    setSearchTerm(term);

    if (term === '') {
      setFilteredPredictions(predictions);
    } else {
      const filtered = predictions.filter((prediction) => {
        return (
          prediction.venue.toLowerCase().includes(term.toLowerCase()) ||
          prediction.race_number.toString().includes(term) ||
          prediction.boat_number.toString().includes(term) ||
          prediction.player_number.toString().includes(term) ||
          prediction.interpretation.toLowerCase().includes(term.toLowerCase())
        );
      });
      setFilteredPredictions(filtered);
    }
  };

  return (
    <div className="prediction-search-container">
      <input
        type="text"
        placeholder="検索キーワードを入力..."
        value={searchTerm}
        onChange={handleSearch}
        className="prediction-search-input"
      />
    </div>
  );
};

export default PredictionSearch;
