function Evaluation() {
  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">

      <h1 className="text-4xl font-bold mb-2">
        Agent Evaluation
      </h1>

      <p className="text-slate-400 mb-8">
        Evaluate the performance and quality of your agent's responses.
      </p>

      {/* Evaluation Summary */}
      <div className="grid grid-cols-3 gap-6 mb-8">

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            Total Evaluations
          </p>

          <h2 className="text-3xl font-bold mt-2">
            0
          </h2>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            Average Score
          </p>

          <h2 className="text-3xl font-bold mt-2">
            0%
          </h2>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            Improvements
          </p>

          <h2 className="text-3xl font-bold mt-2">
            0
          </h2>
        </div>

      </div>

      {/* Evaluation Panel */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h2 className="text-xl font-semibold mb-4">
          Response Evaluation
        </h2>

        <p className="text-slate-400">
          Agent responses will be evaluated based on accuracy,
          relevance, and quality.
        </p>

        <div className="mt-6 flex gap-4">

          <div className="flex-1 bg-slate-800 rounded-lg p-4">
            <p className="text-slate-400 text-sm">
              Accuracy
            </p>

            <p className="text-2xl font-bold mt-2">
              —
            </p>
          </div>

          <div className="flex-1 bg-slate-800 rounded-lg p-4">
            <p className="text-slate-400 text-sm">
              Relevance
            </p>

            <p className="text-2xl font-bold mt-2">
              —
            </p>
          </div>

          <div className="flex-1 bg-slate-800 rounded-lg p-4">
            <p className="text-slate-400 text-sm">
              Overall Quality
            </p>

            <p className="text-2xl font-bold mt-2">
              —
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Evaluation;