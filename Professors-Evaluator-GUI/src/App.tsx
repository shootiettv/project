import { useState } from 'react';
import { ProfessorCard } from './components/ProfessorCard';
import { ComparisonView } from './components/ComparisonView';
import { ProfessorDetailPage } from './components/ProfessorDetailPage';
import { MultiProfessorComparison } from './components/MultiProfessorComparison';
import { ProfessorSelector } from './components/ProfessorSelector';
import { Search, Grid3x3, List } from 'lucide-react';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';

interface Professor {
  id: number;
  name: string;
  department: string;
  rating: number;
  difficulty: number;
  wouldTakeAgain: number;
  imageUrl: string;
}

const mockProfessors: Professor[] = [
  {
    id: 1,
    name: "Dr. Maria Rodriguez",
    department: "Computer Science",
    rating: 4.8,
    difficulty: 3.2,
    wouldTakeAgain: 92,
    imageUrl: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop"
  },
  {
    id: 2,
    name: "Dr. James Chen",
    department: "Engineering",
    rating: 4.5,
    difficulty: 4.1,
    wouldTakeAgain: 85,
    imageUrl: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop"
  },
  {
    id: 3,
    name: "Dr. Sarah Williams",
    department: "Mathematics",
    rating: 4.9,
    difficulty: 3.8,
    wouldTakeAgain: 95,
    imageUrl: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop"
  },
  {
    id: 4,
    name: "Dr. Robert Johnson",
    department: "Physics",
    rating: 4.3,
    difficulty: 4.5,
    wouldTakeAgain: 78,
    imageUrl: "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&h=400&fit=crop"
  },
  {
    id: 5,
    name: "Dr. Emily Martinez",
    department: "Chemistry",
    rating: 4.7,
    difficulty: 3.5,
    wouldTakeAgain: 88,
    imageUrl: "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400&h=400&fit=crop"
  },
  {
    id: 6,
    name: "Dr. Michael Davis",
    department: "Biology",
    rating: 4.6,
    difficulty: 3.9,
    wouldTakeAgain: 90,
    imageUrl: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop"
  }
];

export default function App() {
  const [viewMode, setViewMode] = useState<'grid' | 'detail'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [showComparison, setShowComparison] = useState(false);
  const [selectedProfessor, setSelectedProfessor] = useState<Professor | null>(null);
  const [showMultiComparison, setShowMultiComparison] = useState(false);
  const [showSelector, setShowSelector] = useState(false);
  const [selectedForComparison, setSelectedForComparison] = useState<Professor[]>([]);

  const filteredProfessors = mockProfessors.filter(prof => 
    prof.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prof.department.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggleSelect = (professor: Professor) => {
    setSelectedForComparison(prev => {
      const isSelected = prev.some(p => p.id === professor.id);
      if (isSelected) {
        return prev.filter(p => p.id !== professor.id);
      } else if (prev.length < 3) {
        return [...prev, professor];
      }
      return prev;
    });
  };

  const handleStartComparison = () => {
    setShowSelector(false);
    setShowMultiComparison(true);
  };

  if (selectedProfessor) {
    return (
      <ProfessorDetailPage
        professor={selectedProfessor}
        onBack={() => setSelectedProfessor(null)}
      />
    );
  }

  if (showSelector) {
    return (
      <ProfessorSelector
        professors={mockProfessors}
        selectedProfessors={selectedForComparison}
        onToggleSelect={handleToggleSelect}
        onCompare={handleStartComparison}
        onCancel={() => {
          setShowSelector(false);
          setSelectedForComparison([]);
        }}
      />
    );
  }

  if (showMultiComparison) {
    return (
      <MultiProfessorComparison
        professors={selectedForComparison}
        onBack={() => {
          setShowMultiComparison(false);
          setSelectedForComparison([]);
        }}
      />
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#121212' }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: '#2A2A2A', backgroundColor: '#1E1E1E' }}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="tracking-tight" style={{ color: '#F47A20' }}>
              UTEP Professor Dashboard
            </h1>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSelector(true)}
                style={{
                  backgroundColor: 'transparent',
                  color: '#F47A20',
                  borderColor: '#F47A20',
                  borderRadius: '8px'
                }}
              >
                Compare Professors
              </Button>
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
                className="gap-2"
                style={viewMode === 'grid' ? {
                  backgroundColor: '#F47A20',
                  color: '#EAEAEA',
                  borderColor: '#F47A20'
                } : {
                  backgroundColor: 'transparent',
                  color: '#EAEAEA',
                  borderColor: '#2A2A2A'
                }}
              >
                <Grid3x3 className="w-4 h-4" />
                Grid
              </Button>
              <Button
                variant={viewMode === 'detail' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('detail')}
                className="gap-2"
                style={viewMode === 'detail' ? {
                  backgroundColor: '#F47A20',
                  color: '#EAEAEA',
                  borderColor: '#F47A20'
                } : {
                  backgroundColor: 'transparent',
                  color: '#EAEAEA',
                  borderColor: '#2A2A2A'
                }}
              >
                <List className="w-4 h-4" />
                Detail
              </Button>
            </div>
          </div>
          
          {/* Search Bar */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: '#B0B0B0' }} />
            <Input
              type="text"
              placeholder="Search professors or departments..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 border-0"
              style={{
                backgroundColor: '#2A2A2A',
                color: '#EAEAEA',
                borderRadius: '8px'
              }}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className={viewMode === 'grid' 
          ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          : "flex flex-col gap-4"
        }>
          {filteredProfessors.map(professor => (
            <div key={professor.id} onClick={() => setSelectedProfessor(professor)}>
              <ProfessorCard
                professor={professor}
                viewMode={viewMode}
              />
            </div>
          ))}
        </div>
        
        {filteredProfessors.length === 0 && (
          <div className="text-center py-12" style={{ color: '#B0B0B0' }}>
            No professors found matching your search.
          </div>
        )}
      </main>
    </div>
  );
}