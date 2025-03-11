import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import PredictionTable from './components/PredictionTable';
import PredictionSearch from './components/PredictionSearch';
import './App.css';

function App() {
  const [predictions, setPredictions] = useState([]);
  const [filteredPredictions, setFilteredPredictions] = useState([]);

  // predictionsが更新されたら、フィルタ状態をリセット
  useEffect(() => {
    setFilteredPredictions(predictions);
  }, [predictions]);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Boatrace予想テーブル</h1>
      </header>
      <main>
        <FileUpload setPredictions={setPredictions} />
        {predictions.length > 0 && (
          <>
            <PredictionSearch
              predictions={predictions}
              setFilteredPredictions={setFilteredPredictions}
            />
            <PredictionTable predictions={filteredPredictions} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
