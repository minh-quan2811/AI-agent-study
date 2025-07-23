import React, { useState, useRef, useEffect } from "react";
import axios from "./api";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages(prev => [...prev, userMessage]);

    try {
      const res = await axios.post("/chat", {
        session_id: sessionId,
        message: input,
      });

      const reply = res.data.reply;
      setSessionId(res.data.session_id);

      setMessages(prev => [...prev, { role: "bot", text: reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "bot", text: "❌ Error contacting server" }]);
    }

    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-screen p-4 flex flex-col bg-gray-50">
      <h1 className="text-xl font-bold mb-4">🧠 Chat with LangGraph Bot</h1>
      <div className="flex-1 overflow-auto mb-4 border rounded p-2 bg-white shadow">
        {messages.map((msg, idx) => (
          <div key={idx} className={`my-2 text-${msg.role === "user" ? "right" : "left"}`}>
            <span className={`inline-block p-2 rounded-lg ${msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"}`}>
              {msg.text}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="flex">
        <textarea
          className="flex-1 p-2 border rounded"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage} className="ml-2 px-4 py-2 bg-blue-600 text-white rounded">Send</button>
      </div>
    </div>
  );
}

export default App;
