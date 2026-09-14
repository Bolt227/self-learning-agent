import { useState } from "react";
import Chat from "./Chat";
import Evaluation from "./Evaluation";
import Memory from "./Memory";
import LearningHistory from "./LearningHistory";
function App() {
  const [activePage, setActivePage] = useState("dashboard");
  return (
    <div className="min-h-screen bg-slate-950 text-white flex">

      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900 p-6">

        <h1 className="text-xl font-bold mb-2">
          Self-Learning Agent
        </h1>

        <p className="text-xs text-slate-400 mb-8">
          AI Agent Platform
        </p>

        <nav className="space-y-2">

          <button
            onClick={() => setActivePage("dashboard")}
            className="w-full text-left px-4 py-3 rounded-lg bg-slate-800"
          >
            Dashboard
          </button>

          <button
            onClick={() => setActivePage("chat")}
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800"
          >
            Chat
          </button>

          <button
            onClick={() => setActivePage("evaluation")}
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800"
          >
            Evaluation
          </button>

          <button
            onClick={() => setActivePage("memory")}
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800"
          >
            Memory
          </button>

          <button
            onClick={() => setActivePage("learning")}
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800"
          >
            Learning History
          </button>

        </nav>

      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10">
        {activePage === "chat" ? (
          <Chat />
        ) : activePage === "evaluation" ? (
          <Evaluation />
        ) : activePage === "memory" ? (
          <Memory />
        ) : activePage === "learning" ? (
          <LearningHistory />
        ) : (
          <>

        <h2 className="text-4xl font-bold">
          Agent Dashboard
        </h2>

        <p className="mt-2 text-slate-400">
          Monitor your agent, evaluate its performance,
          and improve its future responses.
        </p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6 mt-8">

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-slate-400">
              Total Interactions
            </p>

            <h3 className="text-3xl font-bold mt-2">
              0
            </h3>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-slate-400">
              Evaluations
            </p>

            <h3 className="text-3xl font-bold mt-2">
              0
            </h3>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-slate-400">
              Learning Updates
            </p>

            <h3 className="text-3xl font-bold mt-2">
              0
            </h3>
          </div>

        </div>

        {/* Agent Status */}
        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">

          <h3 className="text-xl font-semibold">
            Agent Status
          </h3>

          <div className="flex items-center gap-3 mt-5">

            <span className="h-3 w-3 rounded-full bg-green-500"></span>

            <span className="text-slate-300">
              Agent is ready
            </span>

          </div>

        </div>
        </>
        )}
      </main>

    </div>
  )
}

export default App