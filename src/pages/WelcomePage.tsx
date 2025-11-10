import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

export default function WelcomePage() {
  const navigate = useNavigate();

  const handleRestart = () => {
    navigate("/"); // back to start
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <motion.div
        className="w-full max-w-lg"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Card className="text-center dark:bg-gray-800 dark:border-gray-700 shadow-lg">
          <CardHeader>
            <div className="flex justify-center mb-4">
              <CheckCircle2 className="w-16 h-16 text-green-500" />
            </div>
            <CardTitle className="text-3xl font-semibold dark:text-white">
              Automation Complete!
            </CardTitle>
            <CardDescription className="text-gray-600 dark:text-gray-400 mt-2">
              Your UTEP professor data has been successfully retrieved.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="p-4 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300"
            >
              <p className="text-lg font-medium">✅ Process completed successfully</p>
              <p className="text-sm mt-1">
                You can now view or download the results.
              </p>
            </motion.div>

            <div className="flex justify-center space-x-4">
              <Button
                onClick={handleRestart}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Start Over
              </Button>

              <Button
                variant="outline"
                onClick={() => alert("Feature coming soon: view data")}
                className="dark:border-gray-600 dark:text-gray-300"
              >
                View Results
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
