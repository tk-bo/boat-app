import React, { useState } from "react";
import "./FileUpload.css";

const FileUpload = ({ setPredictions }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // ファイル選択時のイベントハンドラ
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    validateFile(selectedFile);
  };

  // ドラッグ＆ドロップ対応
  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    validateFile(droppedFile);
  };

  const validateFile = (selectedFile) => {
    if (!selectedFile) {
      setError("ファイルを選択してください");
      return;
    }
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("ファイルサイズが大きすぎます（最大5MB）");
      return;
    }
    // 拡張子チェックを大文字小文字区別なく行う
    if (!selectedFile.name.toLowerCase().endsWith(".txt")) {
      setError("テキストファイル（.txt）のみアップロードできます");
      return;
    }
    setFile(selectedFile);
    setError("");
  };

  // フォーム送信時のイベントハンドラ
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("ファイルを選択してください");
      return;
    }
    setError("");
    setLoading(true);
    setSuccess(false);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        process.env.REACT_APP_API_URL || "http://localhost:8000/api/upload/",
        {
          method: "POST",
          body: formData,
        }
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPredictions(data.predictions);
      setSuccess(true);
    } catch (error) {
      console.error(error);
      setError("アップロード中にエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* 点線枠のあるアップロードエリア */}
        <div
          className="file-upload-container"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".txt"
            onChange={handleFileChange}
            className="file-upload-input"
            id="fileInput"
          />
          <label htmlFor="fileInput" className="file-upload-label">
            ファイルを選択
          </label>
          {file && (
            <p className="file-upload-file-name">選択されたファイル: {file.name}</p>
          )}
          <p className="file-upload-message">
            または、ここにファイルをドラッグ＆ドロップ
          </p>
        </div>
        {/* ボタンは枠の外に出して中央配置 */}
        <div className="submit-button-container">
          <button
            type="submit"
            className="file-upload-button"
            disabled={loading}
          >
            {loading ? "アップロード中..." : "アップロードして解析"}
          </button>
        </div>
      </form>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">アップロード成功！</p>}
    </div>
  );
};

export default FileUpload;
