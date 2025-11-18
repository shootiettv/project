export interface RateMyProfessorReview {
  rating: number;
  comment: string;
  course: string;
  date: string;
}

export interface RateMyProfessorData {
  overallRating: number;
  wouldTakeAgainPercent: number;
  difficultyRating: number;
  reviews: RateMyProfessorReview[];
  aiSummary: string;
}

export interface Professor {
  id: string;
  name: string;
  department: string;
  rateMyProfessor: RateMyProfessorData;
}