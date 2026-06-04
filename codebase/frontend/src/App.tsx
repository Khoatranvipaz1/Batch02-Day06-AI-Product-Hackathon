import { useState } from "react";
import { sendChatMessage } from "./api";
import "./styles.css";

export default function App() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [isSending, setIsSending] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!message.trim()) {
      return;
    }

    setIsSending(true);
    try {
      const data = await sendChatMessage(message);
      setReply(data.reply);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="app">
      <section className="chat-shell">
        <h1>AI Chatbot</h1>
        <form onSubmit={handleSubmit} className="chat-form">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Type a message..."
          />
          <button type="submit" disabled={isSending}>
            {isSending ? "Sending..." : "Send"}
          </button>
        </form>
        {reply && <p className="reply">{reply}</p>}
      </section>
    </main>
  );
}
