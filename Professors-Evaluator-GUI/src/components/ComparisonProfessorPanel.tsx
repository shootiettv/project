import { Star, Sparkles, ThumbsUp, ThumbsDown } from 'lucide-react';
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

interface ComparisonProfessorPanelProps {
  professor: Professor;
}

export function ComparisonProfessorPanel({ professor }: ComparisonProfessorPanelProps) {
  // Course evaluation data
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

  // AI Summary
  const getAISummary = () => {
    if (professor.rating >= 4.7) {
      return `Outstanding educator with ${professor.rating.toFixed(1)}/5 rating. Students consistently praise clear explanations and engaging lectures. Known for fair grading and strong student support.`;
    } else if (professor.rating >= 4.3) {
      return `Solid instructor with ${professor.rating.toFixed(1)}/5 rating. Delivers well-structured courses with practical focus. Students appreciate organized approach and fair assessments.`;
    } else {
      return `Experienced professor with ${professor.rating.toFixed(1)}/5 rating. Provides comprehensive curriculum coverage. Students note that dedicated study time is required for success.`;
    }
  };

  // Mock reviews
  const positiveReview = {
    text: "Excellent professor! Clear lectures and very approachable. Highly recommend taking this course.",
    rating: 5
  };

  const criticalReview = {
    text: "The pace can be challenging, but you'll learn a lot if you stay on top of the material.",
    rating: 3
  };

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
      <div 
        className="p-6 border-b" 
        style={{ 
          borderColor: '#2A2A2A',
          background: 'linear-gradient(135deg, #1E1E1E 0%, #252525 100%)'
        }}
      >
        <div className="flex flex-col items-center text-center mb-4">
          <ImageWithFallback
            src={professor.imageUrl}
            alt={professor.name}
            className="w-24 h-24 rounded-full object-cover mb-3"
            style={{
              border: '3px solid #F47A20'
            }}
          />
          <h2 className="mb-1" style={{ color: '#EAEAEA' }}>
            {professor.name}
          </h2>
          <p style={{ color: '#0066CC', fontSize: '14px' }}>
            {professor.department}
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center">
            <div className="mb-1" style={{ color: '#B0B0B0', fontSize: '12px' }}>Rating</div>
            <div className="flex flex-col items-center gap-1">
              {renderStars(professor.rating)}
              <span style={{ color: '#F47A20', fontSize: '14px', fontWeight: '600' }}>
                {professor.rating.toFixed(1)}
              </span>
            </div>
          </div>
          <div className="text-center">
            <div className="mb-1" style={{ color: '#B0B0B0', fontSize: '12px' }}>Difficulty</div>
            <div style={{ color: '#EAEAEA', fontSize: '18px', fontWeight: '600' }}>
              {professor.difficulty.toFixed(1)}
            </div>
            <div style={{ color: '#B0B0B0', fontSize: '11px' }}>/ 5.0</div>
          </div>
          <div className="text-center">
            <div className="mb-1" style={{ color: '#B0B0B0', fontSize: '12px' }}>Would Retake</div>
            <div style={{ color: '#FFB84D', fontSize: '18px', fontWeight: '600' }}>
              {professor.wouldTakeAgain}%
            </div>
          </div>
        </div>
      </div>

      {/* AI Summary */}
      <div className="p-5 border-b" style={{ borderColor: '#2A2A2A' }}>
        <div className="flex items-start gap-3 mb-2">
          <Sparkles className="w-4 h-4 flex-shrink-0 mt-1" style={{ color: '#F47A20' }} />
          <h4 style={{ color: '#F47A20', fontSize: '14px', fontWeight: '600' }}>
            AI Summary
          </h4>
        </div>
        <p style={{ color: '#EAEAEA', lineHeight: '1.6', fontSize: '13px' }}>
          {getAISummary()}
        </p>
      </div>

      {/* Course Evaluation Chart */}
      <div className="p-5 border-b" style={{ borderColor: '#2A2A2A' }}>
        <h4 className="mb-4" style={{ color: '#EAEAEA', fontSize: '14px', fontWeight: '600' }}>
          Course Evaluation
        </h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={evaluationData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2A2A" />
            <XAxis type="number" stroke="#B0B0B0" tick={{ fontSize: 11 }} />
            <YAxis 
              type="category" 
              dataKey="category" 
              stroke="#B0B0B0" 
              width={70} 
              tick={{ fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1E1E1E',
                border: '1px solid #0066CC',
                borderRadius: '8px',
                color: '#EAEAEA',
                fontSize: '12px'
              }}
            />
            <Bar dataKey="count" fill="#0066CC" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Sentiment Distribution */}
      <div className="p-5 border-b" style={{ borderColor: '#2A2A2A' }}>
        <h4 className="mb-4" style={{ color: '#EAEAEA', fontSize: '14px', fontWeight: '600' }}>
          Sentiment Distribution
        </h4>
        <ResponsiveContainer width="100%" height={180}>
          <PieChart>
            <Pie
              data={sentimentData}
              cx="50%"
              cy="50%"
              innerRadius={45}
              outerRadius={70}
              paddingAngle={2}
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
                color: '#EAEAEA',
                fontSize: '12px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex items-center justify-center gap-4 mt-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#0066CC' }}></div>
            <span style={{ color: '#B0B0B0', fontSize: '12px' }}>
              Positive ({sentimentData[0].value}%)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#B0B0B0' }}></div>
            <span style={{ color: '#B0B0B0', fontSize: '12px' }}>
              Neutral ({sentimentData[1].value}%)
            </span>
          </div>
        </div>
      </div>

      {/* Review Summary */}
      <div className="p-5">
        <h4 className="mb-4" style={{ color: '#EAEAEA', fontSize: '14px', fontWeight: '600' }}>
          Review Summary
        </h4>
        
        {/* Positive Review */}
        <div className="mb-3">
          <div className="flex items-center gap-2 mb-2">
            <ThumbsUp className="w-4 h-4" style={{ color: '#0066CC' }} />
            <span style={{ color: '#0066CC', fontSize: '12px', fontWeight: '600' }}>
              Top Positive
            </span>
          </div>
          <div
            className="rounded-lg p-3"
            style={{
              backgroundColor: '#121212',
              borderLeft: '3px solid #0066CC',
              borderRadius: '8px'
            }}
          >
            <div className="flex items-center gap-1 mb-1">
              {renderStars(positiveReview.rating)}
            </div>
            <p style={{ color: '#EAEAEA', fontSize: '12px', lineHeight: '1.5' }}>
              "{positiveReview.text}"
            </p>
          </div>
        </div>

        {/* Critical Review */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <ThumbsDown className="w-4 h-4" style={{ color: '#B33A3A' }} />
            <span style={{ color: '#B33A3A', fontSize: '12px', fontWeight: '600' }}>
              Critical Feedback
            </span>
          </div>
          <div
            className="rounded-lg p-3"
            style={{
              backgroundColor: '#121212',
              borderLeft: '3px solid #B33A3A',
              borderRadius: '8px'
            }}
          >
            <div className="flex items-center gap-1 mb-1">
              {renderStars(criticalReview.rating)}
            </div>
            <p style={{ color: '#EAEAEA', fontSize: '12px', lineHeight: '1.5' }}>
              "{criticalReview.text}"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
