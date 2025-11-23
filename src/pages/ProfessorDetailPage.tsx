import { motion } from 'motion/react';
import { ArrowLeft, Star, ThumbsUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Professor, RateMyProfessorReview } from '../App';

interface ProfessorDetailPageProps {
  professor: Professor;
  onBack: () => void;
}

export function ProfessorDetailPage({
  professor,
  onBack,
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

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-blue-50 transition-colors duration-300 p-4">
      {/* Switch Version Button */}
      <div className="fixed bottom-4 left-4 z-50">
        <Button
          variant="outline"
          className="bg-white border-gray-200"
        >
          Switch Version
        </Button>
      </div>

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
              className="bg-white border-gray-200"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to List
            </Button>
            <div className="bg-orange-500 text-white px-6 py-3 rounded-lg shadow-lg">
              <span className="text-2xl">UTEP Professor Ranking</span>
            </div>
          </div>
        </div>

        {/* Professor Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-3xl mb-2">
                  {professor.full_name}
                </CardTitle>
                <p className="text-gray-600">
                  {professor.title}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {professor.department} • {professor.college}
                </p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-2 mb-2">
                  {renderStars(professor.rmp.avgRating)}
                </div>
                <p className="text-3xl text-gray-800">
                  {professor.rmp.avgRating.toFixed(1)}
                </p>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Rate My Professor */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ThumbsUp className="h-5 w-5" />
              Rate My Professor
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Overall Stats */}
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">
                  Overall Rating
                </p>
                <p className="text-3xl text-orange-600">
                  {professor.rmp.avgRating.toFixed(1)}
                </p>
                <div className="flex justify-center gap-1 mt-2">
                  {renderStars(professor.rmp.avgRating)}
                </div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">
                  Would Take Again
                </p>
                <p className="text-3xl text-orange-600">
                  {professor.rmp.wouldTakeAgainPercent}%
                </p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">
                  Difficulty
                </p>
                <p className="text-3xl text-orange-600">
                  {professor.rmp.avgDifficulty.toFixed(1)}
                </p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">
                  Total Ratings
                </p>
                <p className="text-3xl text-orange-600">
                  {professor.rmp.numRatings}
                </p>
              </div>
            </div>

            {/* Class times for this course */}
            {professor.class_sections && professor.class_sections.length > 0 && (
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-gray-900">
                  When this professor is teaching this class upcomming semester
                </h4>
                <div className="space-y-3">
                  {professor.class_sections.map((section, index) => (
                    <div
                      key={section.crn ?? index}
                      className="rounded-xl border border-orange-100 bg-white/80 shadow-sm px-5 py-3 flex flex-col gap-2"
                    >
                      {/* Top row: Section + CRN */}
                      <p className="text-sm font-semibold text-gray-900">
                        <span className="uppercase tracking-wide">
                          Section {section.section ?? 'N/A'}
                        </span>
                        {section.crn && (
                          <span className="ml-3 text-xs font-medium tracking-wide text-gray-400">
                            CRN {section.crn}
                          </span>
                        )}
                      </p>

                      {/* Meeting times */}
                      {(section.meeting_times ?? []).length > 0 ? (
                        <ul className="space-y-1">
                          {section.meeting_times.map((mt, mtIndex) => {
                            const daysValue = mt.days;
                            const days = Array.isArray(daysValue)
                              ? daysValue.join('')
                              : (daysValue ?? '');

                            const locationParts: string[] = [];
                            if (mt.location_building) {
                              locationParts.push(mt.location_building);
                            }
                            if (mt.location_room) {
                              locationParts.push(mt.location_room);
                            }
                            const location = locationParts.join(' ');

                            return (
                              <li
                                key={mtIndex}
                                className="text-sm text-gray-700"
                              >
                                {days && (
                                  <span className="font-medium text-gray-900">
                                    {days}
                                  </span>
                                )}{' '}
                                <span className="font-medium">
                                  {mt.time}
                                </span>
                                {location && (
                                  <>
                                    <span className="mx-1 text-gray-400">
                                      •
                                    </span>
                                    <span className="text-gray-600">
                                      {location}
                                    </span>
                                  </>
                                )}
                              </li>
                            );
                          })}
                        </ul>
                      ) : (
                        <p className="mt-1 text-sm text-gray-600">
                          Meeting time not available yet.
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Reviews */}
            <div className="space-y-4">
              <h4 className="text-gray-800">Recent Reviews</h4>
              {professor.rmp.reviews && professor.rmp.reviews.length > 0 ? (
                professor.rmp.reviews.map((review: RateMyProfessorReview, index) => (
                  <div
                    key={index}
                    className="p-4 bg-gray-50 rounded-lg space-y-2"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex gap-1">
                        {renderStars(review.clarityRating)}
                      </div>
                      <span className="text-sm text-gray-500">
                        {formatDate(review.date)}
                      </span>
                    </div>
                    <p className="text-gray-700">
                      {review.comment}
                    </p>
                    <div className="flex gap-4 text-sm">
                      <p className="text-gray-600">
                        Course:{' '}
                        <span className="text-gray-800">
                          {review.class}
                        </span>
                      </p>
                      <p className="text-gray-600">
                        Difficulty:{' '}
                        <span className="text-gray-800">
                          {review.difficultyRating.toFixed(1)}
                        </span>
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-600 text-center py-4">
                  No reviews available
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center mt-8 text-sm text-gray-600">
          © 2025 University of Texas at El Paso
        </p>
      </motion.div>
    </div>
  );
}
