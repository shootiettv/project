import { motion } from 'motion/react';
import { Moon, Sun, Star, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Professor } from '../types/professor';

interface ProfessorsListPageProps {
  professors: Professor[];
  onSelectProfessor: (professorId: string) => void;
  onSignOut: () => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export function ProfessorsListPage({
  professors,
  onSelectProfessor,
  onSignOut,
  isDarkMode,
  onToggleDarkMode,
}: ProfessorsListPageProps) {
  // Sort professors by rating (highest to lowest)
  const sortedProfessors = [...professors].sort((a, b) =>
    b.rateMyProfessor.overallRating - a.rateMyProfessor.overallRating
  );

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <Star key={i} className="h-5 w-5 fill-orange-500 text-orange-500" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <Star className="h-5 w-5 text-gray-300 dark:text-gray-600" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <Star className="h-5 w-5 fill-orange-500 text-orange-500" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <Star key={i} className="h-5 w-5 text-gray-300 dark:text-gray-600" />
        );
      }
    }
    return stars;
  };

  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300 p-4">
        <motion.div
          className="max-w-6xl mx-auto"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="bg-orange-500 dark:bg-orange-600 text-white px-6 py-3 rounded-lg shadow-lg">
              <span className="text-2xl">UTEP Professor Ranking</span>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={onToggleDarkMode}
                className="rounded-full bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
              >
                {isDarkMode ? (
                  <Sun className="h-5 w-5 text-yellow-500" />
                ) : (
                  <Moon className="h-5 w-5 text-gray-700" />
                )}
              </Button>
              <Button
                variant="outline"
                onClick={onSignOut}
                className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 dark:text-white"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>

          {/* Page Title */}
          <div className="mb-8">
            <h1 className="text-3xl text-gray-800 dark:text-white mb-2">
              Professor Rankings
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Click on a professor to view detailed evaluations
            </p>
          </div>

          {/* Professors Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedProfessors.map((professor, index) => (
              <motion.div
                key={professor.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <Card
                  className="cursor-pointer hover:shadow-lg transition-shadow dark:bg-gray-800 dark:border-gray-700"
                  onClick={() => onSelectProfessor(professor.id)}
                >
                  <CardHeader>
                    <CardTitle className="dark:text-white">
                      {professor.name}
                    </CardTitle>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {professor.department}
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        {renderStars(professor.rateMyProfessor.overallRating)}
                      </div>
                      <p className="text-2xl text-gray-800 dark:text-white">
                        {professor.rateMyProfessor.overallRating.toFixed(2)}
                        <span className="text-sm text-gray-500 dark:text-gray-400 ml-1">
                          / 5.00
                        </span>
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Footer */}
          <p className="text-center mt-8 text-sm text-gray-600 dark:text-gray-400">
            © 2025 University of Texas at El Paso
          </p>
        </motion.div>
      </div>
    </div>
  );
}