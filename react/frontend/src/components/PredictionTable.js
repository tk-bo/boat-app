import React from 'react';

const PredictionTable = ({ predictions }) => {
  return (
    <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse' }}>
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
  );
};

export default PredictionTable;
