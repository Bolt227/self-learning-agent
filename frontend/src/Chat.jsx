import { useState } from "react";

function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message;

    setMessages((prev) => [
        ...prev,
        {
        role: "user",
        content: userMessage,
        },
    ]);

    setMessage("");

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            user_id: "demo_user",
            session_id: "demo_session",
            message: userMessage,
        }),
        });

        const data = await response.json();

        setMessages((prev) => [
        ...prev,
        {
            role: "assistant",
            content: data.response,
        },
        ]);
    } catch (error) {
        console.error("Error:", error);

        setMessages((prev) => [
        ...prev,
        {
            role: "assistant",
            content: "Unable to connect to the agent backend.",
        },
        ]);
    }
    };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <h1 className="text-4xl font-bold mb-2">
        Chat with Agent
      </h1>

      <p className="text-slate-400 mb-8">
        Interact with your self-learning agent.
      </p>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 min-h-[500px] flex flex-col">
        
        <div className="flex-1 space-y-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-slate-500 text-center mt-20">
              Start a conversation with your agent...
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className="bg-slate-800 rounded-lg p-4"
              >
                <div className="text-sm text-slate-400 mb-1">
                  {msg.role === "user" ? "You" : "Agent"}
                </div>

                <div>{msg.content}</div>
              </div>
            ))
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
            placeholder="Ask your agent something..."
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 outline-none focus:border-teal-500"
          />

          <button
            onClick={sendMessage}
            className="bg-teal-600 hover:bg-teal-500 px-6 py-3 rounded-lg font-semibold"
          >
            Send
          </button>
        </div>

      </div>
    </div>
  );
}

export default Chat;