"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setSummary("");

    try {
      const response = await fetch("http://localhost:8000/summary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Unexpected error");
      }

      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-8 bg-gray-50">
      <h1 className="text-2xl font-semibold mb-4 text-gray-900">
        Research Summary Generator
      </h1>

      <textarea
        className="w-full max-w-xl p-3 border rounded-md resize-none h-24 mb-4 text-gray-900"
        placeholder="Ask me something like: AI papers in 2024"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <button
        onClick={handleSubmit}
        disabled={loading || !query.trim()}
        className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800 transition"
      >
        {loading ? "Generating..." : "Generate Summary"}
      </button>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {summary && (
        <div className="mt-8 max-w-xl p-4 bg-white border rounded-md shadow">
          <h2 className="text-lg font-bold mb-2 text-gray-900">Summary</h2>
          <p className="text-gray-800 whitespace-pre-line">{summary}</p>
        </div>
      )}
    </main>
  );
}
