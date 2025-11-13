import { X, Check, Users } from 'lucide-react';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Star } from 'lucide-react';

interface Professor {
  id: number;
  name: string;
  department: string;
  rating: number;
  difficulty: number;
  wouldTakeAgain: number;
  imageUrl: string;
}

interface ProfessorSelectorProps {
  professors: Professor[];
  selectedProfessors: Professor[];
  onToggleSelect: (professor: Professor) => void;
  onCompare: () => void;
  onCancel: () => void;
}

export function ProfessorSelector({
  professors,
  selectedProfessors,
  onToggleSelect,
  onCompare,
  onCancel
}: ProfessorSelectorProps) {
  const isSelected = (professor: Professor) => {
    return selectedProfessors.some(p => p.id === professor.id);
  };

  const canAddMore = selectedProfessors.length < 3;

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className="w-3 h-3"
            fill={star <= Math.floor(rating) ? '#F47A20' : 'none'}
            style={{ color: star <= Math.floor(rating) ? '#F47A20' : '#444' }}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#121212' }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: '#2A2A2A', backgroundColor: '#1E1E1E' }}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="tracking-tight mb-2" style={{ color: '#F47A20' }}>
                Select Professors to Compare
              </h1>
              <p style={{ color: '#B0B0B0', fontSize: '14px' }}>
                Choose up to 3 professors for side-by-side comparison
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onCancel}
              className="gap-2"
              style={{
                backgroundColor: 'transparent',
                color: '#EAEAEA',
                borderColor: '#2A2A2A',
                borderRadius: '8px'
              }}
            >
              <X className="w-4 h-4" />
              Cancel
            </Button>
          </div>
        </div>
      </header>

      {/* Selection Summary Bar */}
      <div
        className="border-b"
        style={{ borderColor: '#2A2A2A', backgroundColor: '#1E1E1E' }}
      >
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5" style={{ color: '#0066CC' }} />
                <span style={{ color: '#EAEAEA', fontSize: '14px', fontWeight: '600' }}>
                  Selected: {selectedProfessors.length} of 3
                </span>
              </div>
              {selectedProfessors.length > 0 && (
                <div className="flex items-center gap-2">
                  {selectedProfessors.map((prof) => (
                    <div
                      key={prof.id}
                      className="flex items-center gap-2 px-3 py-1 rounded-full"
                      style={{
                        backgroundColor: '#0066CC22',
                        border: '1px solid #0066CC',
                        borderRadius: '8px'
                      }}
                    >
                      <span style={{ color: '#0066CC', fontSize: '13px' }}>
                        {prof.name.split(' ')[1]}
                      </span>
                      <button
                        onClick={() => onToggleSelect(prof)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          padding: 0,
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <X className="w-3 h-3" style={{ color: '#0066CC' }} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <Button
              size="sm"
              disabled={selectedProfessors.length < 2}
              onClick={onCompare}
              className="gap-2"
              style={{
                backgroundColor: selectedProfessors.length >= 2 ? '#F47A20' : '#2A2A2A',
                color: selectedProfessors.length >= 2 ? '#FFFFFF' : '#666',
                borderRadius: '8px',
                cursor: selectedProfessors.length >= 2 ? 'pointer' : 'not-allowed'
              }}
            >
              Compare Professors
            </Button>
          </div>
        </div>
      </div>

      {/* Professor Grid */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {professors.map((professor) => {
            const selected = isSelected(professor);
            const disabled = !selected && !canAddMore;

            return (
              <div
                key={professor.id}
                className="rounded-lg p-6 transition-all duration-300 border cursor-pointer"
                style={{
                  backgroundColor: selected ? '#1E1E1E' : disabled ? '#1A1A1A' : '#1E1E1E',
                  borderColor: selected ? '#F47A20' : '#2A2A2A',
                  borderWidth: selected ? '2px' : '1px',
                  boxShadow: selected 
                    ? '0 4px 16px rgba(244, 122, 32, 0.3)' 
                    : '0 2px 8px rgba(0, 0, 0, 0.15)',
                  borderRadius: '8px',
                  opacity: disabled ? 0.5 : 1,
                  cursor: disabled ? 'not-allowed' : 'pointer'
                }}
                onClick={() => {
                  if (!disabled || selected) {
                    onToggleSelect(professor);
                  }
                }}
              >
                <div className="flex flex-col items-center text-center relative">
                  {/* Selection Indicator */}
                  {selected && (
                    <div
                      className="absolute top-0 right-0 rounded-full p-1"
                      style={{
                        backgroundColor: '#F47A20',
                        borderRadius: '50%'
                      }}
                    >
                      <Check className="w-4 h-4" style={{ color: '#FFFFFF' }} />
                    </div>
                  )}

                  <ImageWithFallback
                    src={professor.imageUrl}
                    alt={professor.name}
                    className="w-32 h-32 rounded-full object-cover mb-4"
                    style={{
                      border: selected ? '3px solid #F47A20' : '3px solid transparent'
                    }}
                  />
                  
                  <h3 className="mb-1" style={{ color: '#EAEAEA' }}>
                    {professor.name}
                  </h3>
                  <p className="mb-4" style={{ color: '#0066CC', fontSize: '14px' }}>
                    {professor.department}
                  </p>
                  
                  <div className="w-full space-y-3">
                    <div className="flex items-center justify-between">
                      <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Rating</span>
                      <div className="flex items-center gap-2">
                        {renderStars(professor.rating)}
                        <span style={{ color: '#EAEAEA', fontSize: '13px' }}>
                          {professor.rating.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Difficulty</span>
                      <span style={{ color: '#EAEAEA', fontSize: '13px' }}>
                        {professor.difficulty.toFixed(1)}/5.0
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Would Retake</span>
                      <span style={{ color: '#FFB84D', fontSize: '13px' }}>
                        {professor.wouldTakeAgain}%
                      </span>
                    </div>
                  </div>

                  {/* Select/Deselect Button */}
                  <Button
                    size="sm"
                    className="w-full mt-4 transition-colors"
                    style={{
                      backgroundColor: selected ? '#F47A20' : disabled ? '#2A2A2A' : '#0066CC',
                      color: selected ? '#FFFFFF' : disabled ? '#666' : '#FFFFFF',
                      borderRadius: '8px',
                      cursor: disabled && !selected ? 'not-allowed' : 'pointer'
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (!disabled || selected) {
                        onToggleSelect(professor);
                      }
                    }}
                  >
                    {selected ? 'Selected' : disabled ? 'Max 3 Professors' : 'Select'}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>

        {selectedProfessors.length < 2 && (
          <div
            className="mt-8 rounded-lg p-4 border text-center"
            style={{
              backgroundColor: '#1E1E1E',
              borderColor: '#0066CC',
              borderRadius: '8px'
            }}
          >
            <p style={{ color: '#B0B0B0' }}>
              Select at least 2 professors to start comparing
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
