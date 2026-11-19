import React, { useState, useEffect } from 'react';
import { getAllCareers } from '../apiService';
import './CareerExplorer.css';

function CareerExplorer() {
  const [careers, setCareers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      setError(null);
      getAllCareers()
        .then(response => {
          setCareers(response.data);
        })
        .catch(err => {
          console.error("Error fetching careers:", err);
          setError("Could not load career list.");
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [isOpen]);

  return (
    <div className="career-explorer">
      <button 
        className="btn-primary" 
        onClick={() => setIsOpen(!isOpen)}
        style={{ width: '100%', background: 'var(--primary-hover)' }}
      >
        {isOpen ? 'Hide' : 'Explore All Careers'}
      </button>

      {isOpen && (
        <div className="explorer-content card">
          {loading && <div className="loading">Loading all careers...</div>}
          {error && <div className="error">{error}</div>}
          {!loading && !error && (
            <ul>
              {careers.map((career) => (
                <li key={career.name}>
                  <strong>{career.name}</strong>
                  <p>{career.description}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
export default CareerExplorer;