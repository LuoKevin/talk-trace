type UploadPanelProps = {
  selectedFile: File | null;
  isUploading: boolean;
  onFileChange: (file: File | null) => void;
  onUpload: () => void;
};

export function UploadPanel({
  selectedFile,
  isUploading,
  onFileChange,
  onUpload,
}: UploadPanelProps) {
  return (
    <section className="panel">
      <div>
        <h2>Upload audio</h2>
        <p className="muted">Start with any local audio file. Phase 1 uses fake AI output.</p>
      </div>

      <label className="file-picker">
        <input
          type="file"
          accept="audio/*"
          onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        />
        <span>{selectedFile ? selectedFile.name : "Choose audio file"}</span>
      </label>

      <button disabled={!selectedFile || isUploading} onClick={onUpload}>
        {isUploading ? "Uploading..." : "Create job"}
      </button>
    </section>
  );
}
