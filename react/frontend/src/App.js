import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import PredictionTable from './components/PredictionTable';

function App() {
  const [predictions, setPredictions] = useState([]);

  return (
    <div>
      <h1>テキストファイルアップロード</h1>
      <FileUpload setPredictions={setPredictions} />
      {predictions.length > 0 && <PredictionTable predictions={predictions} />}
    </div>
  );
}

export default App;
