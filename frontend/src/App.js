import { useState } from 'react';

const API = "http://18.227.36.210";
const API_KEY = process.env.REACT_APP_API_KEY || "somesecretrandomstring123";

function ChatTab() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const userMessage = input;
    setInput('');
    setLoading(true);
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);

    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': API_KEY },
      body: JSON.stringify({ message: userMessage })
    });
    const data = await res.json();
    setMessages(prev => [...prev, { role: 'ai', text: data.response }]);
    setLoading(false);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '70vh' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.length === 0 && (
          <p style={{ color: '#666', textAlign: 'center', marginTop: 40 }}>Send a message to start chatting</p>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ textAlign: m.role === 'user' ? 'right' : 'left' }}>
            <span style={{
              background: m.role === 'user' ? '#f97316' : '#1e1e1e',
              color: m.role === 'user' ? 'white' : '#f0f0f0',
              padding: '10px 14px',
              borderRadius: 16,
              display: 'inline-block',
              maxWidth: '80%',
              textAlign: 'left',
              whiteSpace: 'pre-wrap'
            }}>
              {m.text}
            </span>
          </div>
        ))}
        {loading && <p style={{ color: '#666' }}>Thinking...</p>}
      </div>
      <div style={{ display: 'flex', gap: 8, padding: '0 16px 16px' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Type a message..."
          style={{ flex: 1, padding: 12, borderRadius: 8, border: '1px solid #333', background: '#1e1e1e', color: '#f0f0f0', fontSize: 14, outline: 'none' }}
        />
        <button onClick={send} disabled={loading} style={{ padding: '12px 20px', background: '#f97316', color: 'white', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
          Send
        </button>
      </div>
    </div>
  );
}

function RAGTab() {
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);

  async function upload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${API}/upload`, { method: 'POST', headers: { 'x-api-key': API_KEY }, body: form });
    const data = await res.json();
    setUploaded(prev => [...prev, { name: data.filename, chunks: data.chunks }]);
    setUploading(false);
  }

  async function ask() {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer(null);
    const res = await fetch(`${API}/rag-ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': API_KEY },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    setAnswer(data);
    setLoading(false);
  }

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ background: '#1e1e1e', border: '2px dashed #333', borderRadius: 12, padding: 24, textAlign: 'center' }}>
        <p style={{ color: '#888', marginBottom: 12, fontSize: 14 }}>Upload a PDF to add it to your knowledge base</p>
        <label style={{ background: '#f97316', color: 'white', padding: '10px 20px', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 14 }}>
          {uploading ? 'Uploading...' : 'Choose PDF'}
          <input type="file" accept=".pdf" onChange={upload} style={{ display: 'none' }} disabled={uploading} />
        </label>
        {uploaded.length > 0 && (
          <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
            {uploaded.map((f, i) => (
              <p key={i} style={{ color: '#4ade80', fontSize: 13 }}>
                ✓ {f.name} — {f.chunks} chunk{f.chunks !== 1 ? 's' : ''} stored
              </p>
            ))}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && ask()}
          placeholder="Ask a question about your documents..."
          style={{ flex: 1, padding: 12, borderRadius: 8, border: '1px solid #333', background: '#1e1e1e', color: '#f0f0f0', fontSize: 14, outline: 'none' }}
        />
        <button onClick={ask} disabled={loading} style={{ padding: '12px 20px', background: '#f97316', color: 'white', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
          Ask
        </button>
      </div>

      {loading && <p style={{ color: '#666', fontSize: 14 }}>Searching documents...</p>}

      {answer && (
        <div style={{ background: '#1e1e1e', border: '1px solid #2a2a2a', borderRadius: 12, padding: 16 }}>
          <p style={{ whiteSpace: 'pre-wrap', color: '#f0f0f0', lineHeight: 1.6, fontSize: 14 }}>{answer.answer}</p>
          {answer.source && (
            <p style={{ color: '#555', fontSize: 12, marginTop: 12, borderTop: '1px solid #2a2a2a', paddingTop: 8 }}>
              Source: {answer.source}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState('chat');

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh', color: '#f0f0f0', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>
      <div style={{ maxWidth: 700, margin: '0 auto', paddingTop: 40, paddingBottom: 40 }}>
        <h1 style={{ color: '#f97316', textAlign: 'center', marginBottom: 24, fontSize: 22, fontWeight: 700 }}>AI Assistant</h1>

        <div style={{ display: 'flex', borderBottom: '1px solid #222', marginBottom: 0 }}>
          {[['chat', 'Chat'], ['rag', 'Document Q&A']].map(([id, label]) => (
            <button key={id} onClick={() => setTab(id)} style={{
              padding: '12px 24px',
              background: 'none',
              border: 'none',
              color: tab === id ? '#f97316' : '#555',
              borderBottom: tab === id ? '2px solid #f97316' : '2px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: 14,
              marginBottom: -1
            }}>
              {label}
            </button>
          ))}
        </div>

        <div style={{ background: '#111', borderRadius: '0 0 12px 12px', border: '1px solid #222', borderTop: 'none', minHeight: 400 }}>
          {tab === 'chat' ? <ChatTab /> : <RAGTab />}
        </div>
      </div>
    </div>
  );
}
