import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import QuestionnairePage from './pages/QuestionnairePage';
import ResultsPage from './pages/ResultsPage';

// Import our custom-built chatbot
import Chatbot from './components/Chatbot';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <h1>AI Career Predictor</h1>
        <Routes>
          <Route path="/" element={<QuestionnairePage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
        
        {/* Add our custom chatbot component */}
        <Chatbot />
      </div>
    </BrowserRouter>
  );
}

export default App;