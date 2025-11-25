import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { useState } from "react";
import { UploadPage } from "./pages/UploadPage";
import { ClassSelectionPage } from "./pages/ClassSelectionPage";
import { ProfessorListWithSidebar } from "./pages/ProfessorListWithSidebar";
import { ProfessorDetailPage } from "./pages/ProfessorDetailPage";

// export interface Course {
//     code: string;
//     name: string;
//     department: string;
// }

export interface Course {
    _id: string;
    course_title: string
    subject: string
    course_number: string
}

export interface MeetingTime {
  days?: string[] | string;
  time?: string;
  location_building?: string;
  location_room?: string;
}

export interface ClassSectionForProfessor {
  crn?: string;
  section?: string;
  meeting_times: MeetingTime[];
}

export interface Professor {
  _id: string;
  username: string;
  college: string;
  department: string;
  first_name: string;
  full_name: string;
  last_name: number;
  last_updated: number;
  middle_initial: string | null;
  profile_url: string;
  title: string;
  rmp: RateMyProfessorData;

  /** Schedule for THIS course (from Mongo "classes.professors.sections") */
  class_sections?: ClassSectionForProfessor[];
}

export interface RateMyProfessorData {
  avgRating: number;
  avgDifficulty: number;
  numRatings: number;
  wouldTakeAgainPercent: number;
  reviews: RateMyProfessorReview[];
}

export interface RateMyProfessorReview {
  date: string;
  class: string;
  clarityRating: number;
  difficultyRating: number;
  comment: string;
}


// This component can safely use React Router hooks
function AppRoutes() {
  const [classes, setClasses] = useState<any[]>([]);
  const navigate = useNavigate();
  const [selectedClassIds, setSelectedClassIds] = useState<string[]>([]);
  const [professorsByClass, setProfessorsByClass] = useState<Record<string, Professor[]>>({});
  const [selectedProfessor, setSelectedProfessor] = useState<Professor | null>(null);

  


  return (
    <Routes>

      <Route
        path="/"
        element={
          <UploadPage
            onUploadSubmit={(classList) => {
              console.log("📥 App.tsx received classes:", classList);

              setClasses(classList);

              console.log("📦 App.tsx stored classes in state:", classList);

              // Correct navigation (no page reload)
              navigate("/select-classes");
            }}
          />
        }
      />

      <Route
        path="/select-classes"
        element={
          <ClassSelectionPage
            classes={classes}
            onContinue={async (selectedClassIds) => {
              setSelectedClassIds(selectedClassIds);
              const response = await fetch("http://127.0.0.1:8000/get-professors", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ class_ids: selectedClassIds }),
              });

              const data = await response.json();
              setProfessorsByClass(data.professors_by_class);
              navigate("/professors");
            }}


          />
        }
        
      />
      
      <Route
        path="/professors"
        element={
          <ProfessorListWithSidebar
            selectedClasses={classes.filter(c => selectedClassIds.includes(c._id))}
            professorsByClass={professorsByClass}
            onSelectProfessor={(prof) => {
              setSelectedProfessor(prof);
              navigate("/professor-detail");
            }}
            onBack={() => navigate("/select-classes")}
          />
        }
      />
        <Route
          path="/professor-detail"
          element={
            selectedProfessor ? (
              <ProfessorDetailPage
                professor={selectedProfessor}
                onBack={() => navigate("/professors")}
              />
            ) : null
          }
        />

    </Routes>
  );
}

// Wrap AppRoutes in the Router
export default function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}


