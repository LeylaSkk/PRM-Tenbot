import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LayoutDashboard from './components/layout';
import ChatbotInterface from './pages/chat_with_expert';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LayoutDashboard />}>
            <Route path="/" element={<ChatbotInterface/>} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
