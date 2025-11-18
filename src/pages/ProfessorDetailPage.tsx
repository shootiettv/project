import { motion } from 'motion/react';
import { Moon, Sun, ArrowLeft, Star, ThumbsUp } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Professor } from '../types/professor';

interface ProfessorDetailPageProps {
  professor: Professor;
  onBack: () => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export function ProfessorDetailPage({
  professor,
  onBack,
  isDarkMode,
  onToggleDarkMode,
}: ProfessorDetailPageProps) {
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
          className="max-w-5xl mx-auto"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                onClick={onBack}
                className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 dark:text-white"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to List
              </Button>
              <div className="bg-orange-500 dark:bg-orange-600 text-white px-6 py-3 rounded-lg shadow-lg">
                <span className="text-2xl">UTEP Professor Ranking</span>
              </div>
            </div>
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
          </div>

          {/* Professor Header */}
          <Card className="mb-6 dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-3xl dark:text-white mb-2">
                    {professor.name}
                  </CardTitle>
                  <p className="text-gray-600 dark:text-gray-400">
                    {professor.department}
                  </p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-2 mb-2">
                    {renderStars(professor.rateMyProfessor.overallRating)}
                  </div>
                  <p className="text-3xl text-gray-800 dark:text-white">
                    {professor.rateMyProfessor.overallRating.toFixed(2)}
                  </p>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Rate My Professor */}
          <Card className="mb-6 dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <CardTitle className="dark:text-white flex items-center gap-2">
                <ThumbsUp className="h-5 w-5" />
                Rate My Professor
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Overall Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Overall Rating
                  </p>
                  <p className="text-3xl text-orange-600 dark:text-orange-400">
                    {professor.rateMyProfessor.overallRating.toFixed(1)}
                  </p>
                  <div className="flex justify-center gap-1 mt-2">
                    {renderStars(professor.rateMyProfessor.overallRating)}
                  </div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Would Take Again
                  </p>
                  <p className="text-3xl text-orange-600 dark:text-orange-400">
                    {professor.rateMyProfessor.wouldTakeAgainPercent}%
                  </p>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Difficulty
                  </p>
                  <p className="text-3xl text-orange-600 dark:text-orange-400">
                    {professor.rateMyProfessor.difficultyRating.toFixed(1)}
                  </p>
                </div>
              </div>

              {/* AI Summary */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <h4 className="text-sm text-blue-800 dark:text-blue-400 mb-2">
                  AI-Generated Summary
                </h4>
                <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                  {professor.rateMyProfessor.aiSummary}
                </p>
              </div>

              {/* Recent Reviews */}
              <div className="space-y-4">
                <h4 className="text-gray-800 dark:text-white">Recent Reviews</h4>
                {professor.rateMyProfessor.reviews.map((review, index) => (
                  <div
                    key={index}
                    className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg space-y-2"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex gap-1">
                        {renderStars(review.rating)}
                      </div>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {review.date}
                      </span>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300">
                      {review.comment}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Course: {review.course}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <p className="text-center mt-8 text-sm text-gray-600 dark:text-gray-400">
            © 2025 University of Texas at El Paso
          </p>
        </motion.div>
      </div>
    </div>
  );
}