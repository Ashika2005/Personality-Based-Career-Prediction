import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitQuestionnaire } from '../apiService';
import './QuestionnairePage.css';

// --- (All your constants like activityPrefs, problemTypes, etc. go here) ---
const activityPrefs = [
  { value: "A", label: "A. Coding or building software tools" },
  { value: "B", label: "B. Designing visuals or user interfaces" },
  { value: "C", label: "C. Conducting experiments or working with hardware" },
  { value: "D", label: "D. Analyzing financial or business data" },
  { value: "E", label: "E. Planning sustainable or social innovation projects" },
];
const problemTypes = [
  { value: "A", label: "A. Algorithmic / technical challenges" },
  { value: "B", label: "B. Design or user experience problems" },
  { value: "C", label: "C. Real-world environmental or social problems" },
  { value: "D", label: "D. Business or organizational problems" },
  { value: "E", label: "E. Research-oriented theoretical questions" },
];
const motivations = [
  { value: "A", label: "A. Curiosity about how things work" },
  { value: "B", label: "B. The chance to innovate or create something new" },
  { value: "C", label: "C. Seeing the real-world impact of my work" },
  { value: "D", label: "D. Collaborating and managing projects effectively" },
];
const workEnvs = [
  "Solo work with deep focus",
  "Collaborative team projects",
  "Fieldwork / hands-on experimentation",
  "Client interaction and presentations",
  "Creative and flexible workspace",
];
const teamStyles = [
  "I like leading and organizing teams",
  "I’m good at translating complex ideas to simple terms",
  "I prefer technical contributions over social interactions",
  "I enjoy brainstorming and creative collaboration",
];
const toughProblems = [
  { value: "A", label: "A. Break it down logically" },
  { value: "B", label: "B. Visualize the outcome or design" },
  { value: "C", label: "C. Research background and data" },
  { value: "D", label: "D. Discuss it with others for diverse ideas" },
];
const failActions = [
  { value: "A", label: "A. Debug or analyze technical flaws" },
  { value: "B", label: "B. Understand what users didn’t like" },
  { value: "C", label: "C. Check external factors (budget, environment, data)" },
  { value: "D", label: "D. Re-plan and manage tasks better" },
];
const impactPrefs = [
  { value: "A", label: "A. Advance technology & automation" },
  { value: "B", label: "B. Make daily life easier for people" },
  { value: "C", label: "C. Contribute to sustainability or society" },
  { value: "D", label: "D. Inspire creativity and expression" },
  { value: "E", label: "E. Build or lead new ventures" },
];
const projectExcites = [
  { value: "A", label: "A. Developing a new AI model or app" },
  { value: "B", label: "B. Designing an interactive user experience" },
  { value: "C", label: "C. Building a drone or hardware prototype" },
  { value: "D", label: "D. Analyzing large-scale datasets" },
  { value: "E", label: "E. Researching futuristic technologies" },
];
const subjectEngages = [
  "Mathematics / Logic",
  "Physics / Mechanics",
  "Computer Science / AI",
  "Design / Art",
  "Environment / Biology",
  "Business / Economics",
];
const workWiths = [
  { value: "A", label: "A. Code and algorithms" },
  { value: "B", label: "B. Hardware and devices" },
  { value: "C", label: "C. Data and analytics" },
  { value: "D", label: "D. Design tools and creativity suites" },
];


const TOTAL_STEPS = 7;

function QuestionnairePage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    q_logic: 3, q_physical: 3, q_data_patterns: 3, q_creative_visuals: 3, q_social_impact: 3,
    q_activity_pref: "A", q_problem_type: "A", q_motivation: "A",
    q_work_env: [], q_team_style: [],
    q_tough_problem: "A", q_comfort_coding: 3, q_comfort_math: 3, q_comfort_design: 3,
    q_comfort_physics: 3, q_comfort_comms: 3, q_fail_action: "A",
    q_impact_pref: "A", q_project_excite: "A", q_subject_engage: [],
    q_tech_curiosity: 5, q_work_with: "A", q_risk_comfort: 3,
    q_project_hobby: "", q_future_feel: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value, }));
  };
  const handleSliderChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: parseInt(value, 10), }));
  };
  const handleCheckboxChange = (e, fieldName) => {
    const { value, checked } = e.target;
    setFormData((prev) => {
      const currentValues = prev[fieldName];
      let newValues;
      if (checked) {
        newValues = [...currentValues, value];
      } else {
        newValues = currentValues.filter((item) => item !== value);
      }
      return { ...prev, [fieldName]: newValues };
    });
  };

  const nextStep = () => {
    setCurrentStep((prev) => (prev < TOTAL_STEPS ? prev + 1 : prev));
  };
  const prevStep = () => {
    setCurrentStep((prev) => (prev > 1 ? prev - 1 : prev));
  };

  const handleValidateAndNext = () => {
    setError(null);
    let isValid = true;
    
    switch (currentStep) {
      case 3:
        if (formData.q_work_env.length === 0 || formData.q_team_style.length === 0) {
          isValid = false;
          setError("Please select at least one option for each question in this section.");
        }
        break;
      case 5:
        if (formData.q_subject_engage.length === 0) {
          isValid = false;
          setError("Please select at least one subject you find engaging.");
        }
        break;
    }
    
    if (isValid) {
      nextStep();
      window.scrollTo(0, 0);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (formData.q_project_hobby.trim() === "" || formData.q_future_feel.trim() === "") {
        setError("Please fill out the last two text questions.");
        setLoading(false);
        return;
    }

    try {
      const response = await submitQuestionnaire(formData);
      navigate('/results', { state: { prediction: response.data } });
    } catch (err) {
      console.error("Error submitting questionnaire:", err);
      let errorMsg = "Failed to get prediction. Please try again.";
      if (err.response?.data?.detail) {
        errorMsg = `Error: ${JSON.stringify(err.response.data.detail)}`;
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // --- Helper Components ---
  const Slider = ({ label, name, min, max }) => (
    <div className="form-group slider-group">
      <label htmlFor={name}>{label} <span>({formData[name]})</span></label>
      <input type="range" id={name} name={name} min={min} max={max}
        value={formData[name]} onChange={handleSliderChange} />
    </div>
  );
  const Select = ({ label, name, options }) => (
    <div className="form-group">
      <label htmlFor={name}>{label}</label>
      <select id={name} name={name} value={formData[name]} onChange={handleChange}>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
  const CheckboxGroup = ({ label, name, options }) => (
    <div className="form-group checkbox-group">
      <label>{label}</label>
      <div className="checkbox-options">
        {options.map((opt) => (
          <label key={opt} className="checkbox-label">
            <input type="checkbox" name={name} value={opt}
              checked={formData[name].includes(opt)}
              onChange={(e) => handleCheckboxChange(e, name)} />
            {opt}
          </label>
        ))}
      </div>
    </div>
  );
  const ProgressBar = () => {
    const progress = (currentStep / TOTAL_STEPS) * 100;
    return (
      <div className="progress-bar-container">
        <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        <div className="progress-label">Step {currentStep} of {TOTAL_STEPS}</div>
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} className="questionnaire-form">
      <ProgressBar />

      {currentStep === 1 && (
        <div className="card">
          <h3>Section A: Personality & Interest (1-5)</h3>
          <Slider label="I enjoy solving logical or analytical problems." name="q_logic" min="1" max="5" />
          <Slider label="I like designing, building, or improving physical systems." name="q_physical" min="1" max="5" />
          <Slider label="I get excited about discovering patterns from data." name="q_data_patterns" min="1" max="5" />
          <Slider label="I often think about creative ideas (visuals, user experiences)." name="q_creative_visuals" min="1" max="5" />
          <Slider label="I prefer projects with a social or environmental impact." name="q_social_impact" min="1" max="5" />
        </div>
      )}
      {currentStep === 2 && (
        <div className="card">
          <h3>Section B: Skill & Strength</h3>
          <Select label="Which activity sounds most interesting?" name="q_activity_pref" options={activityPrefs} />
          <Select label="What kind of problem do you love solving most?" name="q_problem_type" options={problemTypes} />
          <Select label="What motivates you most to learn?" name="q_motivation" options={motivations} />
        </div>
      )}
      {currentStep === 3 && (
        <div className="card">
          <h3>Section C: Work Preferences</h3>
          <CheckboxGroup label="What type of work environment do you enjoy? (Select all that apply)" name="q_work_env" options={workEnvs} />
          <CheckboxGroup label="Which best describes your teamwork style? (Select all that apply)" name="q_team_style" options={teamStyles} />
        </div>
      )}
      {currentStep === 4 && (
        <div className="card">
          <h3>Section D: Cognitive & Analytical Thinking</h3>
          <Select label="When faced with a tough problem, I first..." name="q_tough_problem" options={toughProblems} />
          <fieldset className="slider-fieldset">
            <legend>Rate your comfort level (1-5)</legend>
            <Slider label="Coding or scripting" name="q_comfort_coding" min="1" max="5" />
            <Slider label="Math / Statistics" name="q_comfort_math" min="1" max="5" />
            <Slider label="Design & Visualization" name="q_comfort_design" min="1" max="5" />
            <Slider label="Physics or Core Engineering" name="q_comfort_physics" min="1" max="5" />
            <Slider label="Communication & Leadership" name="q_comfort_comms" min="1" max="5" />
          </fieldset>
          <Select label="If a project fails, what do you do first?" name="q_fail_action" options={failActions} />
        </div>
      )}
      {currentStep === 5 && (
        <div className="card">
          <h3>Section E: Motivation & Future Vision</h3>
          <Select label="What impact would you like your work to create?" name="q_impact_pref" options={impactPrefs} />
          <Select label="What year-long project would excite you most?" name="q_project_excite" options={projectExcites} />
          <CheckboxGroup label="Which subjects do you find most engaging? (Select all that apply)" name="q_subject_engage" options={subjectEngages} />
        </div>
      )}
      {currentStep === 6 && (
        <div className="card">
          <h3>Section F: Technical Curiosity</h3>
          <Slider label="Curiosity about new tech (AI, AR/VR, etc.)" name="q_tech_curiosity" min="1" max="10" />
          <Select label="Do you prefer working with:" name="q_work_with" options={workWiths} />
          <Slider label="Comfort with risk in projects?" name="q_risk_comfort" min="1" max="5" />
        </div>
      )}
      {currentStep === 7 && (
        <div className="card">
          <h3>Section G: Self-Reflection (Required)</h3>
          <div className="form-group">
            <label htmlFor="q_project_hobby">Describe one project, idea, or hobby that made you feel excited.</label>
            <textarea
              id="q_project_hobby" name="q_project_hobby"
              value={formData.q_project_hobby} onChange={handleChange}
              placeholder="e.g., I built a website that tracks books..."
              rows="4" required
            />
          </div>
          <div className="form-group">
            <label htmlFor="q_future_feel">In one sentence, what do you want your future career to feel like?</label>
            <textarea
              id="q_future_feel" name="q_future_feel"
              value={formData.q_future_feel} onChange={handleChange}
              placeholder="e.g., I want to feel like I'm solving complex puzzles."
              rows="2" required
            />
          </div>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      
      <div className="navigation-buttons">
        <button type="button" className="btn-secondary" onClick={prevStep} disabled={currentStep === 1}>
          Previous
        </button>
        
        {currentStep < TOTAL_STEPS && (
          <button type="button" className="btn-primary" onClick={handleValidateAndNext}>
            Next Section
          </button>
        )}
        
        {currentStep === TOTAL_STEPS && (
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Analyzing...' : 'Predict My Career'}
          </button>
        )}
      </div>
    </form>
  );
}
export default QuestionnairePage;