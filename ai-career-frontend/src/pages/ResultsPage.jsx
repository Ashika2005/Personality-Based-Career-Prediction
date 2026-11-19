import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import ResultsChart from '../components/ResultsChart';
import CareerDetails from '../components/CareerDetails';
import CareerExplorer from '../components/CareerExplorer';
import './ResultsPage.css';

// Simple "Chat" icon
const ChatIcon = () => (
  <svg fill="currentColor" height="24px" width="24px" viewBox="0 0 24 24">
    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"></path>
  </svg>
);

function ResultsPage() {
  const location = useLocation();
  const predictionData = location.state?.prediction;

  if (!predictionData) {
    return (
      <div className="card error">
        <h2>No prediction data found.</h2>
        <p>Please <Link to="/">go back and fill out the questionnaire</Link>.</p>
      </div>
    );
  }

  const { predicted_career, confidence_score, all_scores } = predictionData;

  return (
    <div className="results-page">
      <div className="card prediction-summary">
        <h3>Your Top Recommendation</h3>
        <h1>{predicted_career}</h1>
        <p className="confidence-score">
          Confidence Score: <span>{(confidence_score * 100).toFixed(1)}%</span>
        </p>
      </div>

      <div className="card">
        <h3>Career Compatibility</h3>
        <div className="chart-container">
          <ResultsChart scores={all_scores} />
        </div>
      </div>
      
      <div className="card">
        <CareerDetails careerName={predicted_career} />
      </div>

      <div className="card chat-cta">
        <div className="chat-cta-icon">
          <ChatIcon />
        </div>
        <div className="chat-cta-content">
          <h3>Have Questions? Ask the AI Mentor!</h3>
          <p>
            Use the chat widget in the bottom-right corner to learn more about your results.
          </p>
          <strong>Try asking:</strong>
          <ul>
            <li>"Tell me more about {predicted_career}"</li>
            <li>"What is the learning path for {predicted_career}?"</li>
          </ul>
        </div>
      </div>

      <CareerExplorer />

      <Link to="/" className="btn-primary" style={{marginTop: '20px', display: 'inline-block'}}>
        Take the test again
      </Link>
    </div>
  );
}
export default ResultsPage;