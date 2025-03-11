import React from 'react';
import "./PredictionTable.css";

const PredictionTable = ({ predictions }) => {
  if (!predictions || predictions.length === 0) {
    return <p>予測データがありません。</p>;
  }

  return (
    <div className="prediction-table-container">
      <table className="prediction-table">
        <thead>
          <tr>
            <th>Venue</th>
            <th>Race Number</th>
            <th>Boat Number</th>
            <th>Player Number</th>
            <th>Interpretation</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((prediction, index) => (
            <tr key={index}>
              <td>{prediction.venue}</td>
              <td>{prediction.race_number}</td>
              <td>{prediction.boat_number}</td>
              <td>{prediction.player_number}</td>
              <td>{prediction.interpretation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PredictionTable;
