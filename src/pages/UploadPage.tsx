import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, X, Moon, Sun } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

export default function UploadPage() {
  const navigate = useNavigate();
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // Handle file selection manually or via drag and drop
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setSelectedFile(e.target.files[0]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) setSelectedFile(e.dataTransfer.files[0]);
  };

  // 🧩 Handle upload and trigger FastAPI automation
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return alert("Please select your Degree Evaluation file first.");

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");

      console.log("✅ File uploaded successfully");
      navigate("/loading");
    } catch (err) {
      console.error("❌ Upload failed:", err);
      alert("Something went wrong while uploading your file.");
    } finally {
      setIsUploading(false);
    }
  };


  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300 p-4">
        <div className="w-full max-w-2xl">
          {/* 🌙 Theme Toggle */}
          <div className="flex justify-end mb-4">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="rounded-full bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
            >
              {isDarkMode ? <Sun className="h-5 w-5 text-yellow-500" /> : <Moon className="h-5 w-5 text-gray-700" />}
            </Button>
          </div>

          {/* 🧩 Upload Card */}
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader className="space-y-1">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-orange-500 dark:bg-orange-600 text-white px-6 py-3 rounded-lg">
                  <span className="text-2xl">UTEP Professor Ranking</span>
                </div>
              </div>
              <CardTitle className="text-center dark:text-white">Upload Degree Evaluation</CardTitle>
              <CardDescription className="text-center dark:text-gray-400">
                Please upload your degree evaluation to continue
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label className="dark:text-gray-200">Degree Evaluation File</Label>

                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                      isDragging
                        ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/10'
                        : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                    }`}
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
                    onDrop={handleDrop}
                  >
                    {!selectedFile ? (
                      <div className="space-y-4">
                        <Upload className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto" />
                        <p className="text-gray-700 dark:text-gray-300">
                          Drag and drop your file here, or
                          <label htmlFor="file-upload" className="cursor-pointer text-orange-600 dark:text-orange-400 hover:underline mx-1">
                            browse files
                          </label>
                          <input id="file-upload" type="file" className="hidden" onChange={handleFileChange} accept=".pdf,.doc,.docx,.txt" />
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Supported formats: PDF, DOC, DOCX, TXT
                        </p>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-8 w-8 text-orange-500 dark:text-orange-400" />
                          <div>
                            <p className="text-gray-800 dark:text-gray-200">{selectedFile.name}</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{(selectedFile.size / 1024).toFixed(2)} KB</p>
                          </div>
                        </div>
                        <Button type="button" variant="ghost" size="icon" onClick={() => setSelectedFile(null)}>
                          <X className="h-5 w-5 text-gray-500 hover:text-red-500" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={!selectedFile || isUploading}
                  className="w-full bg-orange-500 hover:bg-orange-600 dark:bg-orange-600 dark:hover:bg-orange-700 text-white disabled:opacity-50"
                >
                  {isUploading ? "Uploading..." : "Submit"}
                </Button>
              </form>
            </CardContent>
          </Card>

          <p className="text-center mt-4 text-sm text-gray-600 dark:text-gray-400">
            © 2025 University of Texas at El Paso
          </p>
        </div>
      </div>
    </div>
  );
}

