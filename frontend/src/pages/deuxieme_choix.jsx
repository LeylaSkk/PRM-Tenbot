import React, { useState } from 'react';
import { AiOutlinePaperClip } from 'react-icons/ai';
import { BsArrowRightCircle, BsCheckCircle } from 'react-icons/bs';

const ChatbotInterface = () => {
  const [input, setInput] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [summary, setSummary] = useState('');
  const [messages, setMessages] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);

  // Handle input change
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() !== '') {
      setSubmitted(true);
      setSummary(`Summary of ${input}...`);
      setMessages([...messages, { sender: 'user', text: input }]);
      setInput('');
    }
  };

  if (!submitted) {
    // Initial interface
    return (
      <div className="flex items-start justify-center min-h-screen bg-gray-100 pt-20 overflow-hidden">
        <div className="w-full max-w-4xl p-8 text-black text-center mx-auto">

          {/* Topic Selection Buttons */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Choose a Topic</h2>
            <div className="flex justify-center gap-6">
              <button 
                onClick={() => setSelectedTopic("Risk Management")}
                className={`w-16 h-16 flex items-center justify-center ${
                  selectedTopic === "Risk Management" ? 'bg-green-500 scale-110' : 'bg-red-500'
                } text-white rounded-full transition-transform transform hover:scale-110`}
              >
                {selectedTopic === "Risk Management" ? <BsCheckCircle size={24} className="text-white" /> : 'RM'}
              </button>
              <button 
                onClick={() => setSelectedTopic("Project Management")}
                className={`w-16 h-16 flex items-center justify-center ${
                  selectedTopic === "Project Management" ? 'bg-green-500 scale-110' : 'bg-blue-900'
                } text-white rounded-full transition-transform transform hover:scale-110`}
              >
                {selectedTopic === "Project Management" ? <BsCheckCircle size={24} className="text-white" /> : 'PM'}
              </button>
            </div>
          </div>

          {/* Chatbot Prompt */}
          <h2 className="text-3xl font-semibold mb-6">What can I help with{selectedTopic ? ` in ${selectedTopic}` : ''}?</h2>

          {/* Input Box */}
          <form onSubmit={handleSubmit} className="flex items-center bg-gray-100 rounded-full px-5 py-3 mb-6 shadow-md">
            <AiOutlinePaperClip className="text-gray-400 mr-3" size={26} />
            <input 
              type="text" 
              placeholder={selectedTopic ? `Ask about ${selectedTopic}` : 'Please select a topic first'} 
              value={input}
              onChange={handleInputChange}
              className="flex-1 bg-transparent text-lg text-gray-700 placeholder-gray-500 focus:outline-none"
              disabled={!selectedTopic}
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
  } else {
    // Next page after message submission
    return (
      <div className="flex w-full h-[90vh] bg-gray-100 p-6 gap-4">
        
        {/* Summary Section */}
        <div className="w-1/2 h-full bg-white flex flex-col rounded-lg shadow-md p-4">
          <h2 className="text-lg font-bold mb-4">Summary</h2>
          <div className="flex-1">
            <p>{summary}</p>
          </div>
        </div>

        {/* Chat Section */}
        <div className="w-1/2 h-full bg-white flex flex-col rounded-lg shadow-md p-4">
          <h2 className="text-lg font-bold mb-4">Chat</h2>
          <div className="flex-1 mb-4">
            {messages.map((msg, index) => (
              <div key={index} className={`mb-4 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                <p className={`${msg.sender === 'user' ? 'bg-blue-100 text-blue-700' : 'bg-gray-200 text-gray-700'} inline-block p-3 rounded-lg`}>
                  {msg.text}
                </p>
              </div>
            ))}
          </div>

          {/* Fixed Input Box at the Bottom */}
          <form onSubmit={handleSubmit} className="flex items-center bg-gray-100 rounded-full px-5 py-3 shadow-md">
            <AiOutlinePaperClip className="text-gray-400 mr-3" size={26} />
            <input 
              type="text" 
              placeholder="Type your message here..." 
              value={input}
              onChange={handleInputChange}
              className="flex-1 bg-transparent text-lg text-gray-700 placeholder-gray-500 focus:outline-none"
            />
            <button type="submit" className="text-gray-400 ml-3 cursor-pointer">
              <BsArrowRightCircle size={30} />
            </button>
          </form>
        </div>
        
      </div>
    );
  }
};

export default ChatbotInterface;
