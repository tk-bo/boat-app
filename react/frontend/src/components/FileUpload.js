import React, { useState } from 'react';

const FileUpload = ({ setPredictions }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');

  // ファイル選択時のイベントハンドラ
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // フォーム送信時のイベントハンドラ
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("ファイルを選択してください");
      return;
    }
    setError("");

    // FormDataにファイルを追加
    const formData = new FormData();
    formData.append('file', file); // API側で "file" というキーを期待している前提

    try {
      const response = await fetch(
        process.env.REACT_APP_API_URL || "http://localhost:8000/api/upload/",
        {
          method: 'POST',
          body: formData,
        }
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // APIのレスポンス（predictions）を親コンポーネントに渡す
      setPredictions(data.predictions);
    } catch (error) {
      console.error(error);
      setError("アップロード中にエラーが発生しました");
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".txt" onChange={handleFileChange} />
        <button type="submit">アップロードして解析</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default FileUpload;
