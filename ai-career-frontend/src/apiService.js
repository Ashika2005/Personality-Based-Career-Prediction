import axios from 'axios';

// Your FastAPI server's base URL
const API_URL = 'http://127.0.0.1:8000';

/**
 * Submits the complete questionnaire to the backend.
 * @param {object} formData - The complete object from your form state.
 * @returns {Promise<object>} The prediction response.
 */
export const submitQuestionnaire = (formData) => {
  return axios.post(`${API_URL}/predict`, formData);
};

/**
 * Fetches the list of all careers.
 * @returns {Promise<Array>} A list of career objects.
 */
export const getAllCareers = () => {
  return axios.get(`${API_URL}/careers`);
};

/**
 * Fetches the learning path for a specific career.
 * @param {string} careerName - The name of the career.
 * @returns {Promise<object>} The learning path object.
 */
export const getLearningPath = (careerName) => {
  return axios.get(`${API_URL}/learning-path/${careerName}`);
};

/**
 * Sends a message to the Gemini-powered chat endpoint.
 * @param {string} message - The user's message.
 * @returns {Promise<object>} The bot's response.
 */
export const sendMessageToChatbot = (message) => {
  return axios.post(`${API_URL}/chat`, { message: message });
};