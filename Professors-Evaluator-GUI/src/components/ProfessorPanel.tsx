import { Star, Sparkles, MessageSquare, ThumbsUp, ThumbsDown, Meh } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';

interface Professor {
  id: number;
  name: string;
  department: string;
  rating: number;
  difficulty: number;
  wouldTakeAgain: number;
  imageUrl: string;
}

interface ProfessorPanelProps {
  professor: Professor;
}

export function ProfessorPanel({ professor }: ProfessorPanelProps) {
  // Mock data for evaluation chart
  const evaluationData = [
    { metric: 'Clarity', value: professor.rating * 20 - 5 },
    { metric: 'Helpfulness', value: professor.rating * 20 + 2 },
    { metric: 'Engagement', value: professor.rating * 18 },
    { metric: 'Grading Fairness', value: professor.rating * 19 },
    { metric: 'Course Material', value: professor.rating * 21 - 8 },
  ];

  // Sentiment data
  const sentimentData = [
    { name: 'Positive', value: professor.wouldTakeAgain, color: '#0066CC' },
    { name: 'Neutral', value: Math.max(0, 100 - professor.wouldTakeAgain - 10), color: '#B0B0B0' },
    { name: 'Negative', value: Math.max(0, 10), color: '#B33A3A' },
  ];

  // AI Summary based on professor data
  const getAISummary = () => {
    if (professor.rating >= 4.7) {
      return `${professor.name.split(' ')[1]} is highly regarded for clear explanations and engaging lectures. Students appreciate the structured approach and fair grading policies. The course material is challenging but rewarding.`;
    } else if (professor.rating >= 4.3) {
      return `${professor.name.split(' ')[1]} delivers solid lectures with a focus on practical applications. Students find the coursework manageable with consistent effort. Office hours are helpful for clarification.`;
    } else {
      return `${professor.name.split(' ')[1]} provides comprehensive coverage of course material. Some students find the pace challenging, but office hours and supplemental resources are available for additional support.`;
    }
  };

  // Mock reviews
  const mockReviews = [
    {
      text: "Excellent professor! Clear lectures and very approachable during office hours.",
      sentiment: "positive"
    },
    {
      text: "Challenging but fair. You'll learn a lot if you put in the effort.",
      sentiment: "positive"
    },
    {
      text: "Tests can be tough, but the professor provides good study materials.",
      sentiment: "neutral"
    }
  ];

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className="w-4 h-4"
            fill={star <= Math.floor(rating) ? '#F47A20' : 'none'}
            style={{ color: star <= Math.floor(rating) ? '#F47A20' : '#444' }}
          />
        ))}
        <span className="ml-1" style={{ color: '#EAEAEA' }}>
          {rating.toFixed(1)}
        </span>
      </div>
    );
  };

  return (
    <div
      className="rounded-lg border overflow-hidden"
      style={{
        backgroundColor: '#1E1E1E',
        borderColor: '#2A2A2A',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
      }}
    >
      {/* Professor Header */}
      <div className="p-6 border-b" style={{ borderColor: '#2A2A2A' }}>
        <div className="flex items-start gap-4 mb-4">
          <ImageWithFallback
            src={professor.imageUrl}
            alt={professor.name}
            className="w-20 h-20 rounded-full object-cover"
          />
          <div className="flex-1">
            <h2 className="mb-1" style={{ color: '#EAEAEA' }}>
              {professor.name}
            </h2>
            <p style={{ color: '#0066CC' }}>
              {professor.department}
            </p>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="mb-1" style={{ color: '#B0B0B0', fontSize: '13px' }}>Rating</div>
            {renderStars(professor.rating)}
          </div>
          <div>
            <div className="mb-1" style={{ color: '#B0B0B0', fontSize: '13px' }}>Difficulty</div>
            <div style={{ color: '#EAEAEA' }}>{professor.difficulty.toFixed(1)}/5.0</div>
          </div>
          <div>
            <div className="mb-1" style={{ color: '#B0B0B0', fontSize: '13px' }}>Would Retake</div>
            <div style={{ color: '#FFB84D' }}>{professor.wouldTakeAgain}%</div>
          </div>
        </div>
      </div>

      {/* AI Summary */}
      <div className="p-6 border-b" style={{ borderColor: '#2A2A2A' }}>
        <div className="flex items-start gap-3 mb-3">
          <Sparkles className="w-5 h-5 flex-shrink-0" style={{ color: '#F47A20' }} />
          <h3 style={{ color: '#F47A20' }}>AI Summary</h3>
        </div>
        <p style={{ color: '#EAEAEA', lineHeight: '1.6' }}>
          {getAISummary()}
        </p>
      </div>

      {/* Charts Section */}
      <div className="p-6 border-b" style={{ borderColor: '#2A2A2A' }}>
        <div className="grid grid-cols-2 gap-6">
          {/* Evaluation Radar Chart */}
          <div>
            <h4 className="mb-4" style={{ color: '#EAEAEA' }}>
              Evaluation Metrics
            </h4>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={evaluationData}>
                <PolarGrid stroke="#2A2A2A" />
                <PolarAngleAxis 
                  dataKey="metric" 
                  tick={{ fill: '#B0B0B0', fontSize: 11 }}
                />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke="#0066CC"
                  fill="#0066CC"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Sentiment Pie Chart */}
          <div>
            <h4 className="mb-4" style={{ color: '#EAEAEA' }}>
              Student Sentiment
            </h4>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="flex items-center justify-center gap-4 mt-2">
              <div className="flex items-center gap-2">
                <ThumbsUp className="w-4 h-4" style={{ color: '#0066CC' }} />
                <span style={{ color: '#B0B0B0', fontSize: '12px' }}>{sentimentData[0].value}%</span>
              </div>
              <div className="flex items-center gap-2">
                <Meh className="w-4 h-4" style={{ color: '#B0B0B0' }} />
                <span style={{ color: '#B0B0B0', fontSize: '12px' }}>{sentimentData[1].value}%</span>
              </div>
              <div className="flex items-center gap-2">
                <ThumbsDown className="w-4 h-4" style={{ color: '#B33A3A' }} />
                <span style={{ color: '#B0B0B0', fontSize: '12px' }}>{sentimentData[2].value}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Review Summary */}
      <div className="p-6">
        <div className="flex items-start gap-3 mb-4">
          <MessageSquare className="w-5 h-5 flex-shrink-0" style={{ color: '#0066CC' }} />
          <h3 style={{ color: '#0066CC' }}>Recent Reviews</h3>
        </div>
        <div className="space-y-3">
          {mockReviews.map((review, index) => (
            <div
              key={index}
              className="rounded-lg p-3"
              style={{ 
                backgroundColor: '#121212', 
                borderLeft: '3px solid #0066CC',
                borderRadius: '8px'
              }}
            >
              <p style={{ color: '#EAEAEA', fontSize: '14px' }}>
                "{review.text}"
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
