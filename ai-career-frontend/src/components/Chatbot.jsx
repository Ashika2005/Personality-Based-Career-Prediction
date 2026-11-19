import React, { useState, useEffect, useRef } from 'react';
import { sendMessageToChatbot } from '../apiService';
import './Chatbot.css';

const SendIcon = () => (
  <svg height="24px" width="24px" viewBox="0 0 24 24">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
  </svg>
);
const ChatIcon = () => (
  <svg height="24px" width="24px" viewBox="0 0 24 24">
    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"></path>
  </svg>
);

function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Hello! I am your AI career mentor. How can I help?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (inputValue.trim() === '') return;

    const userMessage = { from: 'user', text: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendMessageToChatbot(userMessage.text);
      setIsLoading(false);

      if (response.data.response) {
        setMessages((prev) => [...prev, { from: 'bot', text: response.data.response }]);
      } else {
        setMessages((prev) => [...prev, { from: 'bot', text: "Sorry, I didn't understand." }]);
      }
    } catch (error) {
      setIsLoading(false);
      console.error('Error talking to API:', error);
      setMessages((prev) => [...prev, { from: 'bot', text: 'I seem to be having trouble connecting.' }]);
    }
  };

  return (
    <div className="chatbot-container">
      {isOpen && (
        <div className="chat-window card">
          <div className="chat-header">
            <h3>AI Career Mentor</h3>
            <button onClick={toggleChat} className="chat-close-btn">&times;</button>
          </div>
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.from}`}>
                {msg.text}
              </div>
            ))}
            {isLoading && (
              <div className="message bot typing-indicator">
                <span></span><span></span><span></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <form className="chat-input-form" onSubmit={handleSend}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
            />
            <button type="submit" className="chat-send-btn" disabled={isLoading}>
              <SendIcon />
            </button>
          </form>
        </div>
      )}
      <button className="chat-launcher" onClick={toggleChat}>
        <ChatIcon />
      </button>
    </div>
  );
}
export default Chatbot;