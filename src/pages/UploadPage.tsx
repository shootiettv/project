import { useState } from 'react';
import { motion } from 'motion/react';
import { Upload, FileText, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

interface UploadPageProps {
  onUploadSubmit: (classes: any[]) => void;
}

export function UploadPage({ onUploadSubmit }: UploadPageProps) {
  console.log("🔥 UploadPage mounted");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      console.log("📁 File chosen:", e.target.files[0]);
      setSelectedFile(e.target.files[0]);
    } else {
      console.log("❌ No file in event");
    }
  };


  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch("http://127.0.0.1:8000/upload-degree-eval", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    // Pass extracted classes to App.tsx
    console.log("📦 Received from backend:", data);
    console.log("📚 Classes received:", data.classes);
    onUploadSubmit(data.classes);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-blue-50 transition-colors duration-300 p-4">
      {/* Switch Version Button */}
      <div className="fixed bottom-4 left-4">
        <Button
          variant="outline"
          className="bg-white border-gray-200"
        >
          Switch Version
        </Button>
      </div>

      <motion.div 
        className="w-full max-w-2xl"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        {/* Upload Card */}
        <Card>
          <CardHeader className="space-y-1">
            <div className="flex items-center justify-center mb-4">
              <div className="bg-orange-500 text-white px-6 py-3 rounded-lg">
                <span className="text-2xl">UTEP Professor Ranking</span>
              </div>
            </div>
            <CardTitle className="text-center">
              Upload Degree Evaluation
            </CardTitle>
            <CardDescription className="text-center">
              Please upload your degree evaluation to continue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* File Upload Area */}
              <div className="space-y-2">
                <Label>
                  Degree Evaluation File
                </Label>
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    isDragging
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  {!selectedFile ? (
                    <div className="space-y-4">
                      <div className="flex justify-center">
                        <Upload className="h-12 w-12 text-gray-400" />
                      </div>
                      <div className="space-y-2">
                        <p className="text-gray-700">
                          Drag and drop your file here, or
                        </p>
                        <label htmlFor="file-upload" onClick={() => console.log("LABEL CLICKED")}>
                          <span className="text-orange-600 hover:text-orange-700 cursor-pointer underline">
                            browse files
                          </span>
                          <input
                            id="file-upload"
                            type="file"
                            className="hidden"
                            onChange={handleFileChange}
                            accept=".pdf,.doc,.docx,.txt"
                          />
                        </label>
                      </div>
                      <p className="text-sm text-gray-500">
                        Supported formats: PDF, DOC, DOCX, TXT
                      </p>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center space-x-3">
                        <FileText className="h-8 w-8 text-orange-500" />
                        <div className="text-left">
                          <p className="text-gray-800">
                            {selectedFile.name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {(selectedFile.size / 1024).toFixed(2)} KB
                          </p>
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={handleRemoveFile}
                        className="text-gray-500 hover:text-red-600"
                      >
                        <X className="h-5 w-5" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={!selectedFile}
                className="w-full bg-orange-500 hover:bg-orange-600 text-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Submit
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="text-center mt-4 text-sm text-gray-600">
          © 2025 University of Texas at El Paso
        </p>
      </motion.div>
    </div>
  );
}
