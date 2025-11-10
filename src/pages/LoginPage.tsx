import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Moon, Sun } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

export default function LoginPage() {
  const navigate = useNavigate();
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [formData, setFormData] = useState({ username: '', password: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Save credentials to localStorage (or context)
    localStorage.setItem("username", formData.username);
    localStorage.setItem("password", formData.password);
    // Navigate to UploadPage
    navigate("/upload");
  };


  const handleInputChange = (field: string, value: string) =>
    setFormData(prev => ({ ...prev, [field]: value }));

  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300 p-4">
        <div className="w-full max-w-md">
          {/* Theme Toggle */}
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

          {/* Login Card */}
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader className="space-y-1">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-orange-500 dark:bg-orange-600 text-white px-6 py-3 rounded-lg">
                  <span className="text-2xl">UTEP Professor Ranking</span>
                </div>
              </div>
              <CardTitle className="text-center dark:text-white">Sign In</CardTitle>
              <CardDescription className="text-center dark:text-gray-400">
                Enter your UTEP credentials to access your account
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username" className="dark:text-gray-200">UTEP Username</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    className="dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="dark:text-gray-200">UTEP Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className="dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    required
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-orange-500 hover:bg-orange-600 dark:bg-orange-600 dark:hover:bg-orange-700 text-white"
                >
                  Sign In
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

