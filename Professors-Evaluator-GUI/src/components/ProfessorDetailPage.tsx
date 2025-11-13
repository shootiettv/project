import { ArrowLeft, Star, Sparkles, ThumbsUp, ThumbsDown, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

interface Professor {
  id: number;
  name: string;
  department: string;
  rating: number;
  difficulty: number;
  wouldTakeAgain: number;
  imageUrl: string;
}

interface ProfessorDetailPageProps {
  professor: Professor;
  onBack: () => void;
}

export function ProfessorDetailPage({ professor, onBack }: ProfessorDetailPageProps) {
  // Course evaluation data (Excellent to Poor)
  const evaluationData = [
    { category: 'Excellent', count: Math.round(professor.rating * 35) },
    { category: 'Good', count: Math.round(professor.rating * 22) },
    { category: 'Average', count: Math.round((5 - professor.rating) * 15) },
    { category: 'Fair', count: Math.round((5 - professor.rating) * 8) },
    { category: 'Poor', count: Math.round((5 - professor.rating) * 5) },
  ];

  // Sentiment distribution data
  const sentimentData = [
    { name: 'Positive', value: professor.wouldTakeAgain, color: '#0066CC' },
    { name: 'Neutral', value: Math.max(0, 100 - professor.wouldTakeAgain - 8), color: '#B0B0B0' },
    { name: 'Negative', value: 8, color: '#B33A3A' },
  ];

  // Department average comparison
  const departmentAverage = 4.3;
  const satisfactionDiff = ((professor.rating - departmentAverage) / departmentAverage * 100).toFixed(0);

  // AI Summary
  const getAISummary = () => {
    if (professor.rating >= 4.7) {
      return `${professor.name} is an exceptional educator in the ${professor.department} department, consistently praised for clear explanations and engaging teaching style. Students report high levels of understanding and appreciate the structured approach to complex topics. The professor maintains an excellent balance between academic rigor and accessibility, making challenging material approachable through real-world examples and interactive discussions.`;
    } else if (professor.rating >= 4.3) {
      return `${professor.name} delivers solid instruction in ${professor.department} with a practical focus. Students appreciate the organized course structure and fair assessment methods. While the material can be challenging, the professor provides adequate support through office hours and supplementary resources. Overall, students feel well-prepared after completing the course.`;
    } else {
      return `${professor.name} covers comprehensive ${professor.department} curriculum with traditional teaching methods. Students note that coursework requires dedicated study time. The professor provides resources for additional learning and is available during scheduled office hours for questions and clarification on course material.`;
    }
  };

  // Sentiment badge
  const getSentimentBadge = () => {
    if (professor.wouldTakeAgain >= 90) {
      return { text: 'Highly Recommended', color: '#0066CC' };
    } else if (professor.wouldTakeAgain >= 80) {
      return { text: 'Recommended', color: '#0066CC' };
    } else {
      return { text: 'Mixed Reviews', color: '#B0B0B0' };
    }
  };

  const sentiment = getSentimentBadge();

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className="w-5 h-5"
            fill={star <= Math.floor(rating) ? '#F47A20' : 'none'}
            style={{ color: star <= Math.floor(rating) ? '#F47A20' : '#444' }}
          />
        ))}
      </div>
    );
  };

  // Mock positive reviews
  const positiveReviews = [
    {
      text: "Dr. Rodriguez is amazing! Her lectures are clear and she always makes time for students. The projects are challenging but you learn so much.",
      rating: 5,
      course: "CS 3331"
    },
    {
      text: "Best professor I've had at UTEP. Very organized, fair grading, and genuinely cares about student success. Highly recommend!",
      rating: 5,
      course: "CS 4390"
    },
    {
      text: "Excellent teacher who breaks down complex topics into understandable concepts. Office hours are incredibly helpful.",
      rating: 5,
      course: "CS 2302"
    }
  ];

  // Mock critical review
  const criticalReview = {
    text: "The course moves at a fast pace and the exams can be quite difficult. You need to stay on top of the readings and assignments. However, if you put in the work, you'll definitely learn a lot. More practice problems would be helpful.",
    rating: 3,
    course: "CS 3331"
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#121212' }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: '#2A2A2A', backgroundColor: '#1E1E1E' }}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <h1 className="tracking-tight" style={{ color: '#F47A20' }}>
              Professor Profile
            </h1>
            <Button
              variant="outline"
              size="sm"
              onClick={onBack}
              className="gap-2"
              style={{
                backgroundColor: 'transparent',
                color: '#EAEAEA',
                borderColor: '#2A2A2A',
                borderRadius: '8px'
              }}
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Professor Profile Card + AI Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Profile Card */}
          <div
            className="rounded-lg border p-6"
            style={{
              backgroundColor: '#1E1E1E',
              borderColor: '#2A2A2A',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
            }}
          >
            <div className="flex flex-col items-center text-center">
              <ImageWithFallback
                src={professor.imageUrl}
                alt={professor.name}
                className="w-32 h-32 rounded-full object-cover mb-4"
              />
              <h2 className="mb-1" style={{ color: '#EAEAEA' }}>
                {professor.name}
              </h2>
              <p className="mb-6" style={{ color: '#0066CC' }}>
                {professor.department}
              </p>

              {/* Key Stats */}
              <div className="w-full space-y-4">
                <div>
                  <div className="mb-2" style={{ color: '#B0B0B0', fontSize: '13px' }}>Overall Rating</div>
                  <div className="flex items-center justify-center gap-2">
                    {renderStars(professor.rating)}
                    <span style={{ color: '#F47A20' }}>{professor.rating.toFixed(1)}</span>
                  </div>
                </div>

                <div className="pt-4 border-t" style={{ borderColor: '#2A2A2A' }}>
                  <div className="mb-2" style={{ color: '#B0B0B0', fontSize: '13px' }}>Difficulty Level</div>
                  <div style={{ color: '#EAEAEA' }}>{professor.difficulty.toFixed(1)} / 5.0</div>
                </div>

                <div className="pt-4 border-t" style={{ borderColor: '#2A2A2A' }}>
                  <div className="mb-2" style={{ color: '#B0B0B0', fontSize: '13px' }}>Would Take Again</div>
                  <div style={{ color: '#FFB84D' }}>{professor.wouldTakeAgain}%</div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Summary */}
          <div
            className="lg:col-span-2 rounded-lg border p-6"
            style={{
              backgroundColor: '#1E1E1E',
              borderColor: '#2A2A2A',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
            }}
          >
            <div className="flex items-start gap-3 mb-4">
              <Sparkles className="w-6 h-6 flex-shrink-0" style={{ color: '#F47A20' }} />
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 style={{ color: '#F47A20' }}>AI-Generated Summary</h3>
                  <div
                    className="px-3 py-1 rounded-full"
                    style={{
                      backgroundColor: `${sentiment.color}22`,
                      color: sentiment.color,
                      border: `1px solid ${sentiment.color}`,
                      borderRadius: '8px',
                      fontSize: '13px'
                    }}
                  >
                    {sentiment.text}
                  </div>
                </div>
              </div>
            </div>
            <p style={{ color: '#EAEAEA', lineHeight: '1.8' }}>
              {getAISummary()}
            </p>
          </div>
        </div>

        {/* Data Visualizations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Course Evaluation Bar Chart */}
          <div
            className="rounded-lg border p-6"
            style={{
              backgroundColor: '#1E1E1E',
              borderColor: '#0066CC',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
            }}
          >
            <h3 className="mb-6" style={{ color: '#EAEAEA' }}>
              Course Evaluation Distribution
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={evaluationData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2A2A" />
                <XAxis type="number" stroke="#B0B0B0" />
                <YAxis type="category" dataKey="category" stroke="#B0B0B0" width={80} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1E1E1E',
                    border: '1px solid #0066CC',
                    borderRadius: '8px',
                    color: '#EAEAEA'
                  }}
                />
                <Bar dataKey="count" fill="#0066CC" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Sentiment Distribution Pie Chart */}
          <div
            className="rounded-lg border p-6"
            style={{
              backgroundColor: '#1E1E1E',
              borderColor: '#0066CC',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
            }}
          >
            <h3 className="mb-6" style={{ color: '#EAEAEA' }}>
              Student Sentiment Distribution
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1E1E1E',
                    border: '1px solid #0066CC',
                    borderRadius: '8px',
                    color: '#EAEAEA'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex items-center justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#0066CC' }}></div>
                <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Positive</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#B0B0B0' }}></div>
                <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Neutral</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#B33A3A' }}></div>
                <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Negative</span>
              </div>
            </div>
          </div>
        </div>

        {/* Review Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Top 3 Positive Reviews */}
          <div
            className="lg:col-span-2 rounded-lg border p-6"
            style={{
              backgroundColor: '#1E1E1E',
              borderColor: '#2A2A2A',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
            }}
          >
            <div className="flex items-center gap-3 mb-6">
              <ThumbsUp className="w-5 h-5" style={{ color: '#0066CC' }} />
              <h3 style={{ color: '#EAEAEA' }}>Top Positive Reviews</h3>
            </div>
            <div className="space-y-4">
              {positiveReviews.map((review, index) => (
                <div
                  key={index}
                  className="rounded-lg p-4"
                  style={{
                    backgroundColor: '#121212',
                    borderLeft: '3px solid #0066CC',
                    borderRadius: '8px'
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className="w-4 h-4"
                          fill={star <= review.rating ? '#F47A20' : 'none'}
                          style={{ color: star <= review.rating ? '#F47A20' : '#444' }}
                        />
                      ))}
                    </div>
                    <span style={{ color: '#B0B0B0', fontSize: '13px' }}>{review.course}</span>
                  </div>
                  <p style={{ color: '#EAEAEA', lineHeight: '1.6' }}>
                    "{review.text}"
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Critical Review */}
          <div
            className="rounded-lg border p-6"
            style={{
              backgroundColor: '#1E1E1E',
              borderColor: '#2A2A2A',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
            }}
          >
            <div className="flex items-center gap-3 mb-6">
              <ThumbsDown className="w-5 h-5" style={{ color: '#B33A3A' }} />
              <h3 style={{ color: '#EAEAEA' }}>Critical Feedback</h3>
            </div>
            <div
              className="rounded-lg p-4"
              style={{
                backgroundColor: '#121212',
                borderLeft: '3px solid #B33A3A',
                borderRadius: '8px'
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className="w-4 h-4"
                      fill={star <= criticalReview.rating ? '#F47A20' : 'none'}
                      style={{ color: star <= criticalReview.rating ? '#F47A20' : '#444' }}
                    />
                  ))}
                </div>
                <span style={{ color: '#B0B0B0', fontSize: '13px' }}>{criticalReview.course}</span>
              </div>
              <p style={{ color: '#EAEAEA', lineHeight: '1.6' }}>
                "{criticalReview.text}"
              </p>
            </div>
          </div>
        </div>

        {/* Department Comparison Footer */}
        <div
          className="rounded-lg p-5 border"
          style={{
            backgroundColor: '#1E1E1E',
            borderColor: '#0066CC',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
          }}
        >
          <div className="flex items-center justify-center gap-4">
            <TrendingUp className="w-6 h-6" style={{ color: '#0066CC' }} />
            <p style={{ color: '#EAEAEA' }}>
              <span style={{ color: '#B0B0B0' }}>Compared to Department Average:</span>{' '}
              <span style={{ color: '#FFB84D' }}>
                +{satisfactionDiff}% higher satisfaction
              </span>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
