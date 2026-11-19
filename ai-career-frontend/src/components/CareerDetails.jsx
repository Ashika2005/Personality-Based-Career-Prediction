import React, { useState, useEffect } from 'react';
import { getLearningPath, getAllCareers } from '../apiService';
import './CareerDetails.css';

function CareerDetails({ careerName }) {
  const [details, setDetails] = useState(null);
  const [learningPath, setLearningPath] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!careerName) return;
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [pathRes, careersRes] = await Promise.all([
          getLearningPath(careerName),
          getAllCareers()
        ]);
        
        const careerInfo = careersRes.data.find(c => c.name === careerName);
        setDetails(careerInfo);
        setLearningPath(pathRes.data.path);
      } catch (err) {
        console.error("Error fetching career details:", err);
        setError("Could not load career details.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [careerName]);

  if (loading) return <div className="loading">Loading Career Details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!details) return null;

  return (
    <div className="career-details">
      <h3>About {details.name}</h3>
      <p className="career-description">{details.description}</p>
      
      <h4>Recommended Learning Path</h4>
      <ul className="learning-path-list">
        {learningPath.map((item, index) => (
          <li key={index} className="learning-item">
            <span className={`item-type ${item.type.toLowerCase()}`}>{item.type}</span>
            {item.url ? (
              <a href={item.url} target="_blank" rel="noopener noreferrer">
                {item.name}
              </a>
            ) : (
              <span>{item.name}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
export default CareerDetails;