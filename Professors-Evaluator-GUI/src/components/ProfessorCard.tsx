import { Star } from 'lucide-react';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface Professor {
  id: number;
  name: string;
  department: string;
  rating: number;
  difficulty: number;
  wouldTakeAgain: number;
  imageUrl: string;
}

interface ProfessorCardProps {
  professor: Professor;
  viewMode: 'grid' | 'detail';
}

export function ProfessorCard({ professor, viewMode }: ProfessorCardProps) {
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

  if (viewMode === 'detail') {
    return (
      <div
        className="rounded-lg p-6 transition-all duration-300 border cursor-pointer"
        style={{
          backgroundColor: '#1E1E1E',
          borderColor: '#2A2A2A',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          borderRadius: '8px'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.boxShadow = '0 4px 16px rgba(244, 122, 32, 0.2)';
          e.currentTarget.style.borderColor = '#F47A20';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
          e.currentTarget.style.borderColor = '#2A2A2A';
        }}
      >
        <div className="flex gap-6">
          <ImageWithFallback
            src={professor.imageUrl}
            alt={professor.name}
            className="w-24 h-24 rounded-lg object-cover"
          />
          <div className="flex-1">
            <h3 className="mb-1" style={{ color: '#EAEAEA' }}>
              {professor.name}
            </h3>
            <p className="mb-4" style={{ color: '#0066CC' }}>
              {professor.department}
            </p>
            
            <div className="flex items-center gap-6 mb-4">
              <div>
                <div style={{ color: '#B0B0B0', fontSize: '13px' }}>Rating</div>
                {renderStars(professor.rating)}
              </div>
              <div>
                <div style={{ color: '#B0B0B0', fontSize: '13px' }}>Difficulty</div>
                <div style={{ color: '#EAEAEA' }}>{professor.difficulty.toFixed(1)}/5.0</div>
              </div>
              <div>
                <div style={{ color: '#B0B0B0', fontSize: '13px' }}>Would Take Again</div>
                <div style={{ color: '#FFB84D' }}>{professor.wouldTakeAgain}%</div>
              </div>
            </div>
            
            <Button
              size="sm"
              className="transition-colors"
              style={{
                backgroundColor: '#0066CC',
                color: '#EAEAEA',
                borderRadius: '8px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#0077DD';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#0066CC';
              }}
            >
              View Details
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="rounded-lg p-6 transition-all duration-300 border cursor-pointer"
      style={{
        backgroundColor: '#1E1E1E',
        borderColor: '#2A2A2A',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
        borderRadius: '8px'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(244, 122, 32, 0.2)';
        e.currentTarget.style.borderColor = '#F47A20';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
        e.currentTarget.style.borderColor = '#2A2A2A';
      }}
    >
      <div className="flex flex-col items-center text-center">
        <ImageWithFallback
          src={professor.imageUrl}
          alt={professor.name}
          className="w-32 h-32 rounded-full object-cover mb-4"
        />
        
        <h3 className="mb-1" style={{ color: '#EAEAEA' }}>
          {professor.name}
        </h3>
        <p className="mb-4" style={{ color: '#0066CC' }}>
          {professor.department}
        </p>
        
        <div className="w-full space-y-3 mb-4">
          <div className="flex items-center justify-between">
            <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Rating</span>
            {renderStars(professor.rating)}
          </div>
          
          <div className="flex items-center justify-between">
            <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Difficulty</span>
            <span style={{ color: '#EAEAEA' }}>{professor.difficulty.toFixed(1)}/5.0</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span style={{ color: '#B0B0B0', fontSize: '13px' }}>Would Take Again</span>
            <span style={{ color: '#FFB84D' }}>{professor.wouldTakeAgain}%</span>
          </div>
        </div>
        
        <Button
          size="sm"
          className="w-full transition-colors"
          style={{
            backgroundColor: '#0066CC',
            color: '#EAEAEA',
            borderRadius: '8px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#0077DD';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#0066CC';
          }}
        >
          View Details
        </Button>
      </div>
    </div>
  );
}
