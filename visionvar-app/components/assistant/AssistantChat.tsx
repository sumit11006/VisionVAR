'use client';
import { useState, useRef, useEffect } from 'react';
import { usePathname } from 'next/navigation';

export default function AssistantChat() {
  const pathname = usePathname();
  
  // Try to extract session ID from URL (e.g. /sessions/session_vid_123/...)
  let sessionId = undefined;
  let matchId = undefined;
  if (pathname) {
    const match = pathname.match(/\/sessions\/([^\/]+)/);
    if (match) sessionId = match[1];
    
    // For many of our testing flows, the match ID is related to the session ID (or we can pass it if we had it, but sessionId is enough for the LLM to start)
    // The LLM can use get_live_status(sessionId) to get the match_id if needed.
  }

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string, tools?: any[]}[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const endRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    setError(null);
    
    try {
      const res = await fetch('http://localhost:8000/api/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, match_id: matchId, session_id: sessionId })
      });
      
      if (!res.ok) {
        throw new Error('Failed to connect to MCP Assistant');
      }
      
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response, tools: data.tools_used }]);
    } catch (err: any) {
      setError(err.message || 'Connection Error');
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I could not reach the MCP server. Please check your connection.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all z-50 hover:scale-105"
        style={{ background: 'linear-gradient(135deg, #00daf3, #00e479)' }}
      >
        <span className="material-symbols-outlined text-black font-bold text-2xl">
          {isOpen ? 'close' : 'smart_toy'}
        </span>
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div 
          className="fixed bottom-24 right-6 w-[400px] max-w-[90vw] h-[500px] max-h-[80vh] rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden border"
          style={{ background: '#181c22', borderColor: 'rgba(255,255,255,0.1)' }}
        >
          {/* Header */}
          <div className="p-4 border-b flex items-center gap-3" style={{ borderColor: 'rgba(255,255,255,0.05)', background: '#121418' }}>
            <span className="material-symbols-outlined" style={{ color: '#00daf3' }}>smart_toy</span>
            <div>
              <h3 className="font-bold text-sm text-white">VisionVAR Assistant</h3>
              <p className="text-xs text-gray-400">Powered by MCP</p>
            </div>
          </div>
          
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 text-sm mt-10">
                <p>Hello! Ask me anything about the current match, formations, or events.</p>
                <div className="mt-4 flex flex-col gap-2">
                  <button onClick={() => setInput('What was the observed possession?')} className="text-xs bg-[#2a303a] p-2 rounded hover:bg-[#323945] transition-colors">What was the observed possession?</button>
                  <button onClick={() => setInput('Show me the offside incidents.')} className="text-xs bg-[#2a303a] p-2 rounded hover:bg-[#323945] transition-colors">Show me the offside incidents.</button>
                </div>
              </div>
            )}
            
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col max-w-[90%] ${msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'}`}>
                <div 
                  className={`p-3 rounded-2xl text-sm ${msg.role === 'user' ? 'text-black' : 'text-gray-200'} whitespace-pre-wrap`}
                  style={{ background: msg.role === 'user' ? '#00daf3' : '#2a303a', borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px', borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '16px' }}
                >
                  {msg.content}
                </div>
                {msg.tools && msg.tools.length > 0 && (
                  <div className="flex flex-col gap-1 mt-1 text-[10px] text-gray-500">
                    {msg.tools.map((t, j) => (
                      <span key={j} className="flex items-center gap-1">
                        <span className="material-symbols-outlined text-[12px]">construction</span>
                        Consulted MCP: {t.tool}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="self-start items-start bg-[#2a303a] p-3 rounded-2xl rounded-bl-sm text-sm text-gray-400 animate-pulse">
                Analyzing...
              </div>
            )}
            <div ref={endRef} />
          </div>
          
          {/* Error */}
          {error && (
            <div className="px-4 py-2 bg-red-900/30 text-red-400 text-xs text-center border-t border-red-900/50">
              {error}
            </div>
          )}
          
          {/* Input */}
          <form onSubmit={handleSubmit} className="p-3 border-t flex gap-2 items-center" style={{ borderColor: 'rgba(255,255,255,0.05)', background: '#121418' }}>
            <input 
              type="text" 
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask VisionVAR..." 
              className="flex-1 bg-[#181c22] border-none rounded-full px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-[#00daf3]"
            />
            <button 
              type="submit"
              disabled={!input.trim() || isLoading}
              className="w-8 h-8 rounded-full flex items-center justify-center text-black disabled:opacity-50 transition-colors"
              style={{ background: '#00daf3' }}
            >
              <span className="material-symbols-outlined text-sm font-bold">arrow_upward</span>
            </button>
          </form>
        </div>
      )}
    </>
  );
}
