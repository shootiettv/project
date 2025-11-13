import { ArrowLeft, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { ProfessorPanel } from './ProfessorPanel';

interface Professor {
  id: number;
  name: string;
  department: string;
  rating: number;
  difficulty: number;
  wouldTakeAgain: number;
  imageUrl: string;
}

interface ComparisonViewProps {
  professorA: Professor;
  professorB: Professor;
  onBack: () => void;
}

export function ComparisonView({ professorA, professorB, onBack }: ComparisonViewProps) {
  const ratingDiff = professorA.rating - professorB.rating;
  const wouldTakeAgainDiff = professorA.wouldTakeAgain - professorB.wouldTakeAgain;
  
  const getComparisonText = () => {
    if (Math.abs(ratingDiff) < 0.1 && Math.abs(wouldTakeAgainDiff) < 3) {
      return "Both professors are rated similarly with comparable student satisfaction.";
    }
    
    const higherRatedProf = ratingDiff > 0 ? professorA.name.split(' ')[1] : professorB.name.split(' ')[1];
    const ratingText = `${higherRatedProf} rated ${Math.abs(ratingDiff).toFixed(1)} higher overall`;
    
    const higherRetakeProf = wouldTakeAgainDiff > 0 ? professorA.name.split(' ')[1] : professorB.name.split(' ')[1];
    const retakeText = `${Math.abs(wouldTakeAgainDiff)}% more likely to be retaken`;
    
    return `${ratingText} and ${retakeText}.`;
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#121212' }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: '#2A2A2A', backgroundColor: '#1E1E1E' }}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <h1 className="tracking-tight" style={{ color: '#F47A20' }}>
              Professor Comparison
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ProfessorPanel professor={professorA} />
          <ProfessorPanel professor={professorB} />
        </div>

        {/* Comparison Insight Bar */}
        <div
          className="mt-8 rounded-lg p-6 border"
          style={{
            backgroundColor: '#1E1E1E',
            borderColor: '#0066CC',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
          }}
        >
          <div className="flex items-start gap-4">
            <div
              className="rounded-full p-3"
              style={{ 
                backgroundColor: 'rgba(0, 102, 204, 0.2)',
                borderRadius: '8px'
              }}
            >
              <Sparkles className="w-6 h-6" style={{ color: '#0066CC' }} />
            </div>
            <div className="flex-1">
              <h3 className="mb-2" style={{ color: '#F47A20' }}>
                Comparative Insight
              </h3>
              <p style={{ color: '#EAEAEA' }}>
                {getComparisonText()}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
