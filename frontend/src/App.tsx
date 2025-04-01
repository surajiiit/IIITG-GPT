import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, SunMoon, Plus } from 'lucide-react';
import logoImage from './image.png';

interface Message {
  role: 'assistant' | 'user';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isTyping, setIsTyping] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/query', {  // FastAPI backend URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }),
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error fetching response:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error fetching response.' }]);
    }
    
    setIsTyping(false);
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className={`min-h-screen transition-all duration-300 ${isDarkMode ? 'bg-[#0A0A0F]' : 'bg-gray-50'}`}>
      {/* Sidebar */}
      <div className={`fixed top-0 left-0 h-screen w-64 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-800'} p-3 shadow-2xl`}>
        <div className="flex items-center gap-1.5 mb-4">
          <div className="bg-white rounded-lg p-0.5">
            <img src={logoImage} alt="IIITG" className="w-6 h-6 object-contain" />
          </div>
          <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
            IIITG-GPT
          </h1>
        </div>

        <button 
          onClick={clearChat}
          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg p-2 flex items-center gap-2 transition-all duration-300 shadow-lg hover:shadow-blue-500/20"
        >
          <Plus className="w-4 h-4" />
          <span className="font-medium text-sm">New Chat</span>
        </button>
      </div>

      {/* Main Content */}
      <div className="ml-64 h-screen flex flex-col">
        {/* Messages Container */}
        <div 
          className={`flex-1 overflow-y-auto p-3 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}
          style={{ paddingBottom: '80px' }}
        >
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-xl mx-auto p-4 rounded-xl">
                <div className="welcome-icon inline-block p-2 bg-white rounded-xl shadow-lg mb-4">
                  <img src={logoImage} alt="IIITG" className="w-12 h-12 object-contain" />
                </div>
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                  Welcome to IIITG-GPT
                </h2>
                <p className={`text-lg ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Your intelligent assistant powered by IIIT Guwahati
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message-animation flex items-start gap-3 p-4 ${
                    message.role === 'assistant' 
                      ? isDarkMode ? 'bg-gray-900/50' : 'bg-white' 
                      : 'transparent'
                  } mb-3 rounded-xl ${message.role === 'assistant' ? 'shadow-lg' : ''}`}
                >
                  <div className={`rounded-lg ${
                    message.role === 'assistant' 
                      ? 'bg-white p-0.5' 
                      : isDarkMode ? 'bg-gray-700 p-1.5' : 'bg-gray-200 p-1.5'
                  } shadow-lg`}>
                    {message.role === 'assistant' ? (
                      <img src={logoImage} alt="IIITG" className="w-5 h-5 object-contain" />
                    ) : (
                      <User className="w-4 h-4 text-gray-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className={`font-medium text-base mb-1 ${
                      message.role === 'assistant' 
                        ? 'text-blue-500' 
                        : isDarkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      {message.role === 'assistant' ? 'IIITG-GPT' : 'You'}
                    </div>
                    <div className="text-base whitespace-pre-wrap leading-relaxed">
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="message-animation flex items-start gap-3 p-4 bg-gray-900/50 mb-3 rounded-xl">
                  <div className="bg-white p-0.5 rounded-lg shadow-lg">
                    <img src={logoImage} alt="IIITG" className="w-5 h-5 object-contain" />
                  </div>
                  <div className="flex-1">
                    <div className="text-base font-medium text-blue-500 mb-1">IIITG-GPT</div>
                    <div className="flex gap-1.5">
                      <div className="w-1.5 h-1.5 bg-blue-500/50 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                      <div className="w-1.5 h-1.5 bg-blue-500/50 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-1.5 h-1.5 bg-blue-500/50 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Form */}
        <div className={`fixed bottom-0 left-64 right-0 glass-effect ${
          isDarkMode 
            ? 'bg-gray-900/80 border-t border-gray-800' 
            : 'bg-white/80 border-t border-gray-200'
        } p-4`}>
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Send a message..."
              className={`w-full p-3 pr-10 rounded-lg border ${
                isDarkMode 
                  ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-400' 
                  : 'bg-white border-gray-200 text-gray-900'
              } focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 transition-all duration-300 text-base`}
            />
            <button
              type="submit"
              className={`absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg ${
                input.trim() 
                  ? 'text-blue-500 hover:text-blue-600 hover:bg-blue-500/10' 
                  : 'text-gray-400'
              } transition-all duration-300`}
              disabled={!input.trim()}
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className={`fixed top-3 right-3 p-2 rounded-lg ${
            isDarkMode 
              ? 'bg-gray-800 text-blue-400 hover:bg-gray-700' 
              : 'bg-white text-gray-700 hover:bg-gray-100'
          } shadow-lg transition-all duration-300 hover:scale-110`}
        >
          <SunMoon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

export default App;


