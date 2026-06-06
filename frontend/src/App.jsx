import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Upload, 
  FileText, 
  Database, 
  MessageSquare,
  Loader2,
  Paperclip,
  FileSpreadsheet,
  FileJson
} from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = "http://localhost:8001";

const App = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Ready to explore your data. Upload a CSV or PDF to begin." }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_BASE_URL}/upload`, formData);
      if (res.data.error) {
        setMessages(prev => [...prev, { role: 'assistant', content: `Upload failed: ${res.data.error}` }]);
      } else {
        setFiles(prev => [...prev, { name: file.name, type: file.name.split('.').pop().toUpperCase() }]);
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: res.data.message || `Uploaded ${file.name}.` 
        }]);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message || "Upload failed.";
      setMessages(prev => [...prev, { role: 'assistant', content: `Upload failed: ${errorMsg}` }]);
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('message', userMessage);
      const res = await axios.post(`${API_BASE_URL}/chat`, formData);
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response || res.data.error }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Something went wrong. Check your API key." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background text-neutral-400 font-sans">
      {/* Minimal Sidebar */}
      <div className="w-64 border-r border-border flex flex-col bg-surface/50">
        <div className="p-8 pb-4">
          <h1 className="text-white font-semibold tracking-tight text-lg">DataPilot</h1>
          <p className="text-[10px] text-muted uppercase tracking-[0.2em] mt-1">Intelligence</p>
        </div>

        <div className="flex-1 px-4 py-4 space-y-8 overflow-y-auto">
          <section>
            <h3 className="text-[10px] font-bold text-muted uppercase px-4 mb-4 tracking-wider">Sources</h3>
            <div className="space-y-1">
              {files.map((file, i) => (
                <div key={i} className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-white/5 transition-colors group">
                  {file.type === 'CSV' || file.type === 'XLSX' ? <FileSpreadsheet size={14} /> : file.type === 'JSON' ? <FileJson size={14} /> : <FileText size={14} />}
                  <span className="text-xs truncate flex-1">{file.name}</span>
                </div>
              ))}
              <label className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-white/5 cursor-pointer text-neutral-500 hover:text-neutral-300 transition-all group mt-2 border border-dashed border-border/50 mx-2">
                <Paperclip size={14} />
                <span className="text-xs">Attach file</span>
                <input type="file" className="hidden" onChange={handleFileUpload} accept=".csv,.pdf,.xlsx,.json,.txt" />
                {uploading && <Loader2 size={12} className="animate-spin ml-auto" />}
              </label>
            </div>
          </section> 
        </div>

        <div className="p-6 border-t border-border">
          <div className="flex items-center gap-2 px-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/50"></div>
            <span className="text-[10px] text-muted">System Active</span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-8">
        <div className="flex-1 overflow-y-auto pt-12 pb-8 space-y-12">
          {messages.map((msg, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-6 ${msg.role === 'user' ? 'opacity-90' : ''}`}
            >
              <div className="w-8 h-8 rounded border border-border flex-shrink-0 flex items-center justify-center text-[10px] font-bold">
                {msg.role === 'user' ? 'YOU' : 'AI'}
              </div>
              <div className="flex-1 pt-1">
                <p className="text-[14px] leading-relaxed text-neutral-200 whitespace-pre-wrap">{msg.content}</p>
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <div className="flex gap-6 animate-pulse">
              <div className="w-8 h-8 rounded border border-border flex-shrink-0 flex items-center justify-center text-[10px] font-bold text-muted">
                AI
              </div>
              <div className="flex-1 pt-1 flex items-center gap-2">
                <div className="w-1 h-1 bg-muted rounded-full animate-bounce"></div>
                <div className="w-1 h-1 bg-muted rounded-full animate-bounce [animation-delay:0.2s]"></div>
                <div className="w-1 h-1 bg-muted rounded-full animate-bounce [animation-delay:0.4s]"></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="pb-10 pt-4">
          <div className="relative group">
            <div className="absolute inset-0 bg-white/[0.02] rounded-xl border border-border group-focus-within:border-primary/30 transition-colors duration-300"></div>
            <div className="relative flex items-center px-4 py-2">
              <input 
                type="text" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Message DataPilot..."
                className="flex-1 bg-transparent border-none focus:ring-0 outline-none text-[14px] text-neutral-200 placeholder-neutral-600 py-3"
              />
              <button 
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className={`p-2 rounded-lg transition-all ${
                  input.trim() && !isLoading 
                    ? 'text-neutral-200 hover:bg-white/5' 
                    : 'text-neutral-700'
                }`}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
          <p className="text-[9px] text-center mt-4 text-muted tracking-widest uppercase">Hybrid Reasoning Engine</p>
        </div>
      </div>
    </div>
  );
};

export default App;
