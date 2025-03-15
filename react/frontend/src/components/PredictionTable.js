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
            <th>Rank</th>
            <th>Boat Number</th>
            <th>Player Number</th>
            <th>Interpretation</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((prediction, index) => {
            // Race Number が偶数か奇数かでクラスを付与（数値として扱う場合）
            const rowClass =
              Number(prediction.race_number) % 2 === 0 ? 'even-row' : 'odd-row';
            return (
              <tr key={index} className={rowClass}>
                <td>{prediction.venue}</td>
                <td>{prediction.race_number}</td>
                <td>{prediction.rank}</td>
                <td>{prediction.boat_number}</td>
                <td>{prediction.player_number}</td>
                <td>{prediction.interpretation}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default PredictionTable;
