import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useRef } from "react";

export default function LoadingPage() {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("Starting automation...");

  useEffect(() => {
    const hasStartedRef = useRef(false); // ✅ stays constant between re-renders

    if (!hasStartedRef.current) {
      hasStartedRef.current = true;
      const username = localStorage.getItem("username") ?? "";
      const password = localStorage.getItem("password") ?? "";

      // Step 1️⃣ Start automation
      fetch("http://127.0.0.1:8000/run", {
        method: "POST",
        body: new URLSearchParams({ username, password }),
      }).catch(err => console.error("❌ Automation start failed:", err));
    }


    // Step 2️⃣ Poll progress every second
    const interval = setInterval(async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/progress");
        const data = await res.json();
        setProgress(data.progress);
        setStatus(data.status);

        if (data.progress >= 100) {
          clearInterval(interval);
          navigate("/welcome");
        }
      } catch (err) {
        console.error("❌ Failed to fetch progress:", err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-4 transition-colors duration-300">
      <div className="w-full max-w-lg">
        <Card className="dark:bg-gray-800 dark:border-gray-700">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-2xl dark:text-white">Loading Professor Data...</CardTitle>
            <CardDescription className="dark:text-gray-400">
              Please wait while we connect to UTEP systems and fetch course data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Progress value={progress} className="h-4 w-full bg-gray-200 dark:bg-gray-700" />
            <div className="text-center text-gray-700 dark:text-gray-300">
              <p className="text-sm">{status}</p>
              <p className="mt-1 font-semibold text-lg">{progress}%</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

