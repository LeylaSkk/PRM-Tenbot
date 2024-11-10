import React, { useState, useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { AiOutlinePaperClip } from "react-icons/ai";
import { BsArrowRightCircle, BsCheckCircle } from "react-icons/bs";
import {
  Paperclip,
  ArrowRightCircle,
  CheckCircle,
  Plus,
  MessageSquare,
} from "lucide-react";
import {
  FaMicrophone,
  FaImage,
  FaQuestionCircle,
  FaRegClock,
  FaCog,
  FaSignOutAlt 
} from "react-icons/fa";

const ChatbotInterface = () => {
  const { loginWithRedirect, isAuthenticated } = useAuth0();
  const { logout } = useAuth0();
  const { user } = useAuth0();

  const [showModal, setShowModal] = useState(!isAuthenticated);

  const [input, setInput] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [summary, setSummary] = useState("");
  const [messages, setMessages] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [activeTab, setActiveTab] = useState("chat");
  const [newMessage, setNewMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [imagePreview, setImagePreview] = useState(null); // State for image preview
  const [clickedTab, setClickedTab] = useState(null);
  const profilePicture = user?.picture; // Profile picture URL from Google
  const sendMessageToBackend = async (message) => {
    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      const data = await response.json();
      if (response.ok) {
        return data.response;
      } else {
        console.error('Error:', data.error);
        return 'Sorry, I encountered an error processing your request.';
      }
    } catch (error) {
      console.error('Network error:', error);
      return 'Sorry, I cannot connect to the server at the moment.';
    }
  };
  const handleTabClick = (tab) => {
    if (tab === "chat") {
      setActiveTab(tab);
    } else {
      setClickedTab(tab);
      setTimeout(() => setClickedTab(null), 200); // Briefly shows blue styling on click
    }
  };
  let recognition;

  useEffect(() => {
    if (!isAuthenticated) {
      setShowModal(true);
    }
  }, [isAuthenticated]);

  // Check if SpeechRecognition is available
  if ("webkitSpeechRecognition" in window) {
    recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join("");
      setNewMessage(transcript);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };
  } else {
    console.warn("Speech Recognition is not supported in this browser");
  }

  // Define handleMicrophoneClick function
  const handleMicrophoneClick = () => {
    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
    } else {
      recognition.start();
      setIsRecording(true);
    }
  };
  // New state for conversations
  const [conversations, setConversations] = useState([
    {
      id: 1,
      title: "Risk Assessment Discussion",
      date: "Nov 8",
      preview: "Discussing project risks...",
    },
    {
      id: 2,
      title: "Project Timeline Analysis",
      date: "Nov 8",
      preview: "Analyzing delivery schedules...",
    },
    {
      id: 3,
      title: "Budget Planning",
      date: "Nov 7",
      preview: "Review of Q4 budget...",
    },
  ]);
  const [selectedConversation, setSelectedConversation] = useState(null);

  // Handle input change
  const handleInputChange = (e) => {
    if (!isAuthenticated) {
      // Trigger login modal if not authenticated
      loginWithRedirect();
      return;
    }
    setInput(e.target.value);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      loginWithRedirect();
      return;
    }
  
    if (input.trim() !== "") {
      setSubmitted(true);
      setMessages([...messages, { sender: "user", text: input }]);
      
      // Send message to backend and get response
      const botResponse = await sendMessageToBackend(input);
      setMessages(prev => [...prev, { sender: "bot", text: botResponse }]);
      
      setInput("");
    }
  };
  // Handle starting a new chat
  const handleNewChat = () => {
    if (!isAuthenticated) {
      // Trigger login modal if not authenticated
      loginWithRedirect();
      return;
    }

    setSelectedConversation(null);
    setMessages([]);
    setInput("");
  };

  // Handle new message submission (e.g., sending message with an image)
  const handleNewMessageSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      loginWithRedirect();
      return;
    }

    if (newMessage.trim() !== "") {
      setMessages(prev => [...prev, { sender: "user", text: newMessage }]);
      
      // Send message to backend and get response
      const botResponse = await sendMessageToBackend(newMessage);
      setMessages(prev => [...prev, { sender: "bot", text: botResponse }]);
      
      if (imagePreview) {
        setImagePreview(null);
      }
      setNewMessage("");
    }
  };
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImagePreview(URL.createObjectURL(file)); // Set image preview URL
    }
  };

  const LoginModal = () => (
    <div className="fixed inset-0 bg-gray-700 bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg text-center">
        <h2 className="text-2xl font-bold mb-4">Please log in</h2>
        <p className="mb-6">You need to log in to continue.</p>
        <button
          onClick={() => loginWithRedirect()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Log in
        </button>
      </div>
    </div>
  );

  if (!submitted) {
    // Initial interface
    return (
      <div>
              {!isAuthenticated && <LoginModal />}
              {isAuthenticated && (

      <div className="flex items-start justify-center min-h-screen pt-20 overflow-hidden">
        <div className="w-full max-w-4xl p-8 text-black text-center mx-auto">
          {/* Topic Selection Buttons */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Choose a Topic</h2>
            <div className="flex justify-center gap-6">
              <button
                onClick={() => setSelectedTopic("Risk Management")}
                className={`w-16 h-16 flex items-center justify-center ${
                  selectedTopic === "Risk Management"
                    ? "bg-green-500 scale-110"
                    : "bg-red-500"
                } text-white rounded-full transition-transform transform hover:scale-110`}
              >
                {selectedTopic === "Risk Management" ? (
                  <BsCheckCircle size={24} className="text-white" />
                ) : (
                  "RM"
                )}
              </button>
              <button
                onClick={() => setSelectedTopic("Project Management")}
                className={`w-16 h-16 flex items-center justify-center ${
                  selectedTopic === "Project Management"
                    ? "bg-green-500 scale-110"
                    : "bg-blue-900"
                } text-white rounded-full transition-transform transform hover:scale-110`}
              >
                {selectedTopic === "Project Management" ? (
                  <BsCheckCircle size={24} className="text-white" />
                ) : (
                  "PM"
                )}
              </button>
            </div>
          </div>

          {/* Chatbot Prompt */}
          <h2 className="text-3xl font-semibold mb-6">
            What can I help with{selectedTopic ? ` in ${selectedTopic}` : ""}?
          </h2>

          {/* Input Box */}
          <form
            onSubmit={handleSubmit}
            className="flex items-center bg-gray-100 rounded-full px-5 py-3 mb-6 shadow-md"
          >
            <AiOutlinePaperClip className="text-gray-400 mr-3" size={26} />
            <input
              type="text"
              placeholder={
                selectedTopic
                  ? `Ask about ${selectedTopic}`
                  : "Please select a topic first"
              }
              value={input}
              onChange={handleInputChange}
              className="flex-1 bg-transparent text-lg text-gray-700 placeholder-gray-500 focus:outline-none"
              disabled={!selectedTopic}
            />
            <button
              type="submit"
              className="text-gray-400 ml-3 cursor-pointer"
              disabled={!selectedTopic}
            >
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
       )}
      </div>

    );
  } else {
    return (
      <div
        className={`flex h-[92vh] bg-white ${
          activeTab === "chat" ? "grow" : ""
        }`}
      >
        {/* Sidebar */}
        {activeTab === "chat" && (
          <div className="fixed h-full w-1/5 bg-gray-300 border-r border-gray-200 flex flex-col p-4 left-0">
            {/* Start New Chat Button */}
            <button
              onClick={handleNewChat}
              className="p-3 mb-6 flex items-center justify-center gap-2 text-white rounded-lg hover:bg-blue-950 transition-colors bg-blue-900/90"
            >
              <Plus size={20} />
              Start New Chat
            </button>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto mt-4">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => setSelectedConversation(conversation)}
                  className={`w-full p-4 text-left hover:bg-gray-400 px-4 rounded flex items-start gap-3 ${
                    selectedConversation?.id === conversation.id
                      ? "bg-gray-400"
                      : ""
                  } text-white`}
                >
                  <MessageSquare size={20} className="text-red-700 mt-1" />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-sm text-gray-700 truncate">
                      {conversation.title}
                    </h3>
                    <p className="text-sm text-gray-700 truncate">
                      {conversation.preview}
                    </p>
                  </div>
                </button>
              ))}
            </div>

            {/* Bottom Section */}
            <div className="border-t border-gray-400 pt-4 text-gray-700 mb-16">
              <button className="flex items-center gap-2 py-2 w-full text-left hover:bg-gray-400 px-4 rounded">
                <FaQuestionCircle size={20} className="text-gray-700" />
                Help
              </button>
              <button className="flex items-center gap-2 py-2 w-full text-left hover:bg-gray-400 px-4 rounded">
                <FaRegClock size={20} className="text-gray-700" />
                Activity
              </button>
              <button className="flex items-center gap-2 py-2 w-full text-left hover:bg-gray-400 px-4 rounded">
                <FaCog size={20} className="text-gray-700" />
                Settings
              </button>
              <button onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                className="flex items-center gap-2 py-2 w-full text-left hover:bg-gray-400 px-4 rounded text-gray-700"
              >
                <FaSignOutAlt size={20} className="text-gray-700" />
                Log Out
              </button>
            </div>
          </div>
        )}

        {/* Main Content */}

        <div
          className={`flex flex-col grow bg-gray-200 ${
            activeTab === "chat" ? "ml-[20%]" : ""
          }`}
        >
          {/* Tab Buttons */}
          <div className="border-b border-gray-200">
            <div className="py-4">
              <div className="flex justify-center gap-4">
                {["chat", "flashcards", "summary"].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => handleTabClick(tab)}
                    className={`px-6 py-2 rounded-full font-medium transition-colors ${
                      activeTab === tab || clickedTab === tab
                        ? "bg-blue-900 text-white"
                        : "text-gray-600 hover:text-red-700"
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
          {/* Chat Content */}
          {activeTab === "chat" && (
            <div className="flex-1 overflow-y-auto py-4 px-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`mb-4 flex items-end ${
                    message.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`inline-block p-3 rounded-lg ${
                      message.sender === "user"
                        ? "bg-gray-600 text-white"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {message.text}
                  </div>
                  {message.sender === "user" && (
                    <img
                      src={user?.picture || "https://via.placeholder.com/40"}
                      alt="User Profile"
                      className="w-8 h-8 rounded-full ml-2"
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Input Box */}
          {activeTab === "chat" && (
            <div className="border-t border-gray-200 bg-gray-200">
              <div className="p-4 flex justify-center">
                <form
                  onSubmit={handleNewMessageSubmit}
                  className="relative w-2/3"
                >
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Ask el m3allem"
                    className="w-full p-3 pr-16 rounded-full bg-white text-black placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-900"
                  />
                  {imagePreview && (
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="w-10 h-10 rounded-full mr-2"
                      />
                    </div>
                  )}
                  <div className="absolute inset-y-0 right-3 flex items-center gap-2">
                    <label className="text-gray-400 cursor-pointer">
                      <FaImage size={20} />
                      <input
                        type="file"
                        onChange={handleFileUpload} // Image upload handler
                        className="hidden"
                      />
                    </label>
                    <FaMicrophone
                      className={`text-gray-400 cursor-pointer ${
                        isRecording ? "text-red-500" : ""
                      }`}
                      size={20}
                      onClick={handleMicrophoneClick}
                    />
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }
};

export default ChatbotInterface;
