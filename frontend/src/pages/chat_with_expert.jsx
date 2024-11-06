import React, { useState } from 'react';
import { AiOutlinePaperClip } from 'react-icons/ai';
import { BsArrowRightCircle, BsCheckCircle } from 'react-icons/bs';

const ChatbotInterface = () => {
  const [input, setInput] = useState(''); // Tracks the input message
  const [submitted, setSubmitted] = useState(false); // Tracks if a message was submitted
  const [selectedTopic, setSelectedTopic] = useState(null); // Tracks the chosen topic

  // Handle input change
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() !== '') {
      setSubmitted(true); // Switch to the "response" page
    }
  };

  // Handle topic selection
  const handleTopicSelection = (topic) => {
    setSelectedTopic(topic);
  };

  return (
    <div className="flex items-start justify-center min-h-screen bg-gray-100 pt-40 overflow-hidden">
      <div className="w-full max-w-4xl p-10 text-black text-center mx-auto">

        {/* Topic Selection Buttons */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Choose a Topic</h2>
          <div className="flex justify-center gap-6">
            <button 
              onClick={() => handleTopicSelection('Risk Management')} 
              className={`w-16 h-16 flex items-center justify-center ${
                selectedTopic === 'Risk Management' ? 'bg-green-500 scale-110' : 'bg-red-500'
              } text-white rounded-full transition-transform transform hover:scale-110`}
            >
              {selectedTopic === 'Risk Management' ? (
                <BsCheckCircle size={24} className="text-white" />
              ) : (
                'RM'
              )}
            </button>
            <button 
              onClick={() => handleTopicSelection('Project Management')} 
              className={`w-16 h-16 flex items-center justify-center ${
                selectedTopic === 'Project Management' ? 'bg-green-500 scale-110' : 'bg-blue-900'
              } text-white rounded-full transition-transform transform hover:scale-110`}
            >
              {selectedTopic === 'Project Management' ? (
                <BsCheckCircle size={24} className="text-white" />
              ) : (
                'PM'
              )}
            </button>
          </div>
        </div>

        {/* Chatbot Prompt */}
        <h2 className="text-3xl font-semibold mb-6">
          What can I help with{selectedTopic ? ` in ${selectedTopic}` : ''}?
        </h2>

        {/* Input Box */}
        <form onSubmit={handleSubmit} className="flex items-center bg-gray-100 rounded-full px-5 py-3 mb-6 shadow-md">
          <AiOutlinePaperClip className="text-gray-400 mr-3" size={26} />
          <input 
            type="text" 
            placeholder={selectedTopic ? `Ask about ${selectedTopic}` : 'Please select a topic first'} 
            value={input}
            onChange={handleInputChange}
            className="flex-1 bg-transparent text-lg text-gray-700 placeholder-gray-500 focus:outline-none"
            disabled={!selectedTopic} // Disable input until a topic is selected
          />
          <button type="submit" className="text-gray-400 ml-3 cursor-pointer" disabled={!selectedTopic}>
            <BsArrowRightCircle size={30} />
          </button>
        </form>

        {/* Options */}
        <div className="flex justify-center flex-wrap gap-4">
          <button className="px-5 py-2 text-sm font-medium text-black rounded-full hover:bg-gray-300 transition">
            <span className="text-green-400 mr-1">●</span> Create image
          </button>
          <button className="px-5 py-2 text-sm font-medium text-black rounded-full hover:bg-gray-300 transition">
            <span className="text-purple-400 mr-1">●</span> Help me write
          </button>
          <button className="px-5 py-2 text-sm font-medium text-black rounded-full hover:bg-gray-300 transition">
            <span className="text-yellow-400 mr-1">●</span> Make a plan
          </button>
          <button className="px-5 py-2 text-sm font-medium text-black rounded-full hover:bg-gray-300 transition">
            <span className="text-orange-400 mr-1">●</span> Summarize text
          </button>
          <button className="px-5 py-2 text-sm font-medium text-black rounded-full hover:bg-gray-300 transition">
            <span className="text-blue-400 mr-1">●</span> More
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotInterface;
