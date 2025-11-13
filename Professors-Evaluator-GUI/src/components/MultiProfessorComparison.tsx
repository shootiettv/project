import { ArrowLeft, Sparkles, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';
import { ComparisonProfessorPanel } from './ComparisonProfessorPanel';

interface Professor {
  id: number;
  name: string;
  department: string;
  rating: number;
  difficulty: number;
  wouldTakeAgain: number;
  imageUrl: string;
}

interface MultiProfessorComparisonProps {
  professors: Professor[];
  onBack: () => void;
}

export function MultiProfessorComparison({ professors, onBack }: MultiProfessorComparisonProps) {
  // Generate AI comparison summary
  const getAICompareSummary = () => {
    if (professors.length === 0) return "";
    
    // Find best rated
    const bestRated = professors.reduce((prev, current) => 
      current.rating > prev.rating ? current : prev
    );
    
    // Find easiest
    const easiest = professors.reduce((prev, current) => 
      current.difficulty < prev.difficulty ? current : prev
    );
    
    // Find highest would take again
    const mostRetaken = professors.reduce((prev, current) => 
      current.wouldTakeAgain > prev.wouldTakeAgain ? current : prev
    );
    
    const parts = [];
    
    if (bestRated.rating === Math.max(...professors.map(p => p.rating))) {
      parts.push(`${bestRated.name.split(' ')[1]} has the best overall rating (${bestRated.rating.toFixed(1)})`);
    }
    
    if (easiest.difficulty === Math.min(...professors.map(p => p.difficulty))) {
      parts.push(`${easiest.name.split(' ')[1]} has the easiest grading (difficulty ${easiest.difficulty.toFixed(1)})`);
    }
    
    if (mostRetaken.wouldTakeAgain === Math.max(...professors.map(p => p.wouldTakeAgain))) {
      parts.push(`${mostRetaken.wouldTakeAgain}% of students would retake ${mostRetaken.name.split(' ')[1]}'s course`);
    }
    
    return parts.join('; ') + '.';
  };

  // Generate footer insight
  const getFooterInsight = () => {
    if (professors.length === 0) return "";
    
    const departmentAverage = 4.3;
    const bestPerformer = professors.reduce((prev, current) => 
      current.rating > prev.rating ? current : prev
    );
    
    const satisfactionDiff = ((bestPerformer.rating - departmentAverage) / departmentAverage * 100).toFixed(0);
    
    return `${bestPerformer.name.split(' ')[1]}'s students report +${satisfactionDiff}% higher satisfaction than department average.`;
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#121212' }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: '#2A2A2A', backgroundColor: '#1E1E1E' }}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <h1 className="tracking-tight" style={{ color: '#F47A20' }}>
              Compare Professors
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
        {/* AI Compare Summary Bar */}
        <div
          className="rounded-lg p-5 mb-8"
          style={{
            backgroundColor: '#F47A20',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
          }}
        >
          <div className="flex items-start gap-4">
            <div
              className="rounded-full p-2"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '8px'
              }}
            >
              <Sparkles className="w-6 h-6" style={{ color: '#FFFFFF' }} />
            </div>
            <div className="flex-1">
              <h3 className="mb-1" style={{ color: '#FFFFFF', fontWeight: '600' }}>
                AI Comparison Summary
              </h3>
              <p style={{ color: '#FFFFFF', lineHeight: '1.6' }}>
                {getAICompareSummary()}
              </p>
            </div>
          </div>
        </div>

        {/* 3-Column Comparison Grid */}
        <div className={`grid gap-6 mb-8 ${
          professors.length === 1 ? 'grid-cols-1 max-w-2xl mx-auto' :
          professors.length === 2 ? 'grid-cols-1 lg:grid-cols-2' :
          'grid-cols-1 lg:grid-cols-2 xl:grid-cols-3'
        }`}>
          {professors.map((professor) => (
            <ComparisonProfessorPanel key={professor.id} professor={professor} />
          ))}
        </div>

        {/* Footer Insight Bar */}
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
              <span style={{ color: '#B0B0B0', fontWeight: '500' }}>Key Insight:</span>{' '}
              <span style={{ color: '#FFB84D' }}>
                {getFooterInsight()}
              </span>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
