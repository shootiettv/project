import { useState } from 'react';
import { motion } from 'motion/react';
import { Star, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Professor, Course } from '../App';

interface ProfessorListWithSidebarProps {
  selectedClasses: Course[];
  professorsByClass: Record<string, Professor[]>;
  onSelectProfessor: (professor: Professor) => void;
  onBack: () => void;
}

export function ProfessorListWithSidebar({
  selectedClasses,
  professorsByClass,
  onSelectProfessor,
  onBack,
}: ProfessorListWithSidebarProps) {
  const [activeClass, setActiveClass] = useState<string>(selectedClasses[0]?._id || '');
  const [searchQuery, setSearchQuery] = useState("");
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <Star key={i} className="h-4 w-4 fill-orange-500 text-orange-500" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <Star className="h-4 w-4 text-gray-300 dark:text-gray-600" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <Star className="h-4 w-4 fill-orange-500 text-orange-500" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <Star key={i} className="h-4 w-4 text-gray-300 dark:text-gray-600" />
        );
      }
    }
    return stars;
  };
  const getMeetingSummary = (prof: Professor) => {
    const sections = prof.class_sections ?? [];
    const allMeetings = sections.flatMap((section) => section.meeting_times ?? []);

    if (allMeetings.length === 0) {
      return null;
    }

    const first = allMeetings[0];
    const daysValue = first.days;
    const days = Array.isArray(daysValue)
      ? daysValue.join('')
      : (daysValue ?? '');

    const locationParts: string[] = [];
    if (first.location_building) locationParts.push(first.location_building);
    if (first.location_room) locationParts.push(first.location_room);
    const location = locationParts.join(' ');

    return {
      label: `${days ? days + ' ' : ''}${first.time ?? ''}`,
      location,
      extraCount: allMeetings.length - 1,
    };
  };

  const currentClassInfo = selectedClasses.find((c) => c._id === activeClass);
  const currentProfessorsRaw = professorsByClass[activeClass] || [];
  const currentProfessors = currentProfessorsRaw.filter((prof) =>
    prof.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );


  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-blue-50 transition-colors duration-300">
      {/* Switch Version Button */}
      <div className="fixed bottom-4 left-4 z-50">
        <Button
          variant="outline"
          className="bg-white border-gray-200"
        >
          Switch Version
        </Button>
      </div>

      <div className="flex h-screen">
        {/* Sidebar */}
        <motion.div
          className="w-64 bg-white border-r border-gray-200 overflow-y-auto"
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg text-gray-800">
              Your Classes
            </h2>
            <p className="text-xs text-gray-600 mt-1">
              {selectedClasses.length} selected
            </p>
          </div>
          <div className="p-2">
            {selectedClasses.map((course) => (
              <button
                key={course._id}
                onClick={() => setActiveClass(course._id)}
                className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${
                  activeClass === course._id
                    ? 'bg-orange-500 text-white'
                    : 'hover:bg-gray-100 text-gray-800'
                }`}
              >
                <div className="text-sm">{course._id}</div>
                <div className="text-xs opacity-80 mt-1 truncate">
                  {course.course_title}
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          <motion.div
            className="p-6"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          >
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
              <div className="bg-orange-500 text-white px-6 py-3 rounded-lg shadow-lg">
                <span className="text-2xl">UTEP Professor Ranking</span>
              </div>
                {/* Search Bar */}
                <input
                  type="text"
                  placeholder="Search professors..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm w-64 focus:ring-2 focus:ring-orange-400 focus:outline-none"
                />
              <Button
                variant="outline"
                onClick={onBack}
                className="bg-white border-gray-200"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </div>

            {/* Class Info */}
            {currentClassInfo && (
              <div className="mb-6">
                <h1 className="text-3xl text-gray-800 mb-2">
                  {currentClassInfo._id} - {currentClassInfo.course_title}
                </h1>
                <p className="text-gray-600">
                  Professors ranked by recommendation
                </p>
              </div>
            )}

                        {/* Professors List */}
            <div className="space-y-4">
              {currentProfessors.length > 0 ? (
                currentProfessors.map((professor, index) => {
                  const meetingInfo = getMeetingSummary(professor);

                  return (
                    <motion.div
                      key={professor._id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                    >
                      <Card
                        className="cursor-pointer hover:shadow-lg transition-shadow"
                        onClick={() => onSelectProfessor(professor)}
                      >
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <div>
                              <CardTitle>
                                {professor.full_name}
                              </CardTitle>
                              <p className="text-sm text-gray-600 mt-1">
                                {professor.title} • {professor.department}
                              </p>
                            </div>
                            <div className="text-right">
                              <div className="flex items-center gap-1 mb-1">
                                {renderStars(professor.rmp.avgRating)}
                              </div>
                              <p className="text-2xl text-gray-800">
                                {professor.rmp.avgRating.toFixed(1)}
                              </p>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="flex flex-col gap-2 text-sm">
                            <div className="flex flex-wrap gap-4">
                              <div>
                                <span className="text-gray-600">
                                  Difficulty:
                                </span>
                                <span className="ml-1 text-gray-800">
                                  {professor.rmp.avgDifficulty.toFixed(1)}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-600">
                                  Would Take Again:
                                </span>
                                <span className="ml-1 text-gray-800">
                                  {professor.rmp.wouldTakeAgainPercent}%
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-600">
                                  Ratings:
                                </span>
                                <span className="ml-1 text-gray-800">
                                  {professor.rmp.numRatings}
                                </span>
                              </div>
                            </div>

                            {meetingInfo && (
                              <div className="text-gray-600">
                                <span className="font-medium text-gray-700">
                                  Class time:
                                </span>{" "}
                                <span className="text-gray-800">
                                  {meetingInfo.label}
                                  {meetingInfo.location && ` • ${meetingInfo.location}`}
                                </span>
                                {meetingInfo.extraCount > 0 && (
                                  <span className="ml-1 text-xs text-gray-500">
                                    (+{meetingInfo.extraCount} more time
                                    {meetingInfo.extraCount > 1 ? 's' : ''})
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })
              ) : (
                <Card>
                  <CardContent className="p-8 text-center">
                    <p className="text-gray-600">
                      No professors found for this class
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>


            {/* Footer */}
            <p className="text-center mt-8 text-sm text-gray-600">
              © 2025 University of Texas at El Paso
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}