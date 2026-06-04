import "./App.css";
import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import InputBar from "./components/InputBar";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { messages, loading, send, newConversation, bottomRef } = useChat();

  return (
    <div className="app">
      <Header onNew={newConversation} />
      <main className="main">
        <ChatWindow messages={messages} loading={loading} bottomRef={bottomRef} />
        <InputBar onSend={send} loading={loading} />
      </main>
    </div>
  );
}
