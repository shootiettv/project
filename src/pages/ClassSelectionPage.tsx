import { useState } from 'react';
import { motion } from 'motion/react';
import { Check, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Course } from '../App';

interface ClassSelectionPageProps {
  classes: Course[];
  onContinue: (selectedClasses: string[]) => void;
}

export function ClassSelectionPage({

  classes,
  onContinue,
}: ClassSelectionPageProps) {
  console.log("📘 ClassSelectionPage props:", classes);

  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);

  // Group classes by department
  const groupedClasses = classes.reduce((acc, course) => {
    if (!acc[course.subject]) {
      acc[course.subject] = [];
    }
    acc[course.subject].push(course);
    return acc;
  }, {} as Record<string, Course[]>);

  const toggleClass = (classCode: string) => {
    setSelectedClasses((prev) =>
      prev.includes(classCode)
        ? prev.filter((c) => c !== classCode)
        : [...prev, classCode]
    );
  };

  const handleContinue = () => {
    if (selectedClasses.length > 0) {
      onContinue(selectedClasses);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-blue-50 transition-colors duration-300 p-4">
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
        className="max-w-6xl mx-auto"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div className="bg-orange-500 text-white px-6 py-3 rounded-lg shadow-lg">
            <span className="text-2xl">UTEP Professor Ranking</span>
          </div>
        </div>

        {/* Page Title */}
        <div className="mb-6">
          <h1 className="text-3xl text-gray-800 mb-2">
            Select Your Classes
          </h1>
          <p className="text-gray-600">
            Choose the classes you'd like to take next semester
          </p>
        </div>

        {/* Continue Button at Top */}
        <div className="flex justify-center mb-8">
          <Button
            onClick={handleContinue}
            disabled={selectedClasses.length === 0}
            size="lg"
            className="bg-orange-500 hover:bg-orange-600 text-white disabled:opacity-50"
          >
            Continue with {selectedClasses.length} class{selectedClasses.length !== 1 ? 'es' : ''}
            <ChevronRight className="ml-2 h-5 w-5" />
          </Button>
        </div>

        {/* Classes by Department */}
        <div className="space-y-8 mb-6">
          {Object.entries(groupedClasses).map(([department, courses], deptIndex) => (
            <motion.div
              key={department}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: deptIndex * 0.1 }}
            >
              <h2 className="text-xl text-gray-800 mb-4">
                {department} - {courses[0].course_title.split(' ')[0]} Department
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {courses.map((course, index) => {
                  const isSelected = selectedClasses.includes(course._id);
                  return (
                    <motion.div
                      key={course._id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      <Card
                        className={`cursor-pointer transition-all hover:shadow-lg ${
                          isSelected
                            ? 'ring-2 ring-orange-500 bg-orange-50'
                            : ''
                        }`}
                        onClick={() => toggleClass(course._id)}
                      >
                        <CardHeader className="pb-3">
                          <div className="flex justify-between items-start">
                            <CardTitle className="text-lg">
                              {course._id}
                            </CardTitle>
                            {isSelected && (
                              <div className="bg-orange-500 rounded-full p-1">
                                <Check className="h-4 w-4 text-white" />
                              </div>
                            )}
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-gray-600">
                            {course.course_title}
                          </p>
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Footer */}
        <p className="text-center mt-8 text-sm text-gray-600">
          © 2025 University of Texas at El Paso
        </p>
      </motion.div>
    </div>
  );
}