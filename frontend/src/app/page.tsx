// frontend/src/app/page.tsx
"use client";

import { useState } from "react";
import ModeSelector from "./components/ModeSelector";

// Define interfaces for the paper data
interface Paper {
  title: string;
  category: string;
  year: number;
  month: number;
  summary: string;
}

export default function Home() {
  const [queryMode, setQueryMode] = useState<'rollup' | 'filtering'>('rollup');
  const [query, setQuery] = useState("");
  const [summary, setSummary] = useState("");
  const [filteredPapers, setFilteredPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setSummary("");
    setFilteredPapers([]);

    try {
      if (queryMode === 'rollup') {
        const response = await fetch("http://localhost:8000/summary", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query, mode: queryMode }),
        });

        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || "Unexpected error");
        }

        const data = await response.json();
        setSummary(data.summary);
      } else {
        const response = await fetch("http://localhost:8000/filter", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query, mode: queryMode }),
        });

        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || "Unexpected error");
        }

        const data = await response.json();
        setFilteredPapers(data.papers);
      }
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
        Research Paper Explorer
      </h1>

      <div className="w-full max-w-xl flex gap-4 mb-4">
        <textarea
          className="flex-1 p-3 border rounded-md resize-none h-24 text-gray-900"
          placeholder={
            queryMode === 'rollup' 
              ? "Ask me something like: AI papers in 2024" 
              : "Enter search terms like: Show me Machine Learning papers from March 2024"
          }
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <ModeSelector mode={queryMode} onModeChange={setQueryMode} />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !query.trim()}
        className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800 transition"
      >
        {loading ? "Processing..." : queryMode === 'rollup' ? "Generate Summary" : "Filter Papers"}
      </button>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {/* Results Section */}
      <div className="mt-8 w-full max-w-xl">
        {/* Roll-up Results */}
        {queryMode === 'rollup' && summary && (
          <div className="p-4 bg-white border rounded-md shadow">
            <h2 className="text-lg font-bold mb-2 text-gray-900">Summary</h2>
            <p className="text-gray-800 whitespace-pre-line">{summary}</p>
          </div>
        )}

        {/* Filtering Results */}
        {queryMode === 'filtering' && filteredPapers.length > 0 && (
          <div>
            <h2 className="text-lg font-bold mb-4 text-gray-900">
              Found Papers ({filteredPapers.length})
            </h2>
            <div className="space-y-4">
              {filteredPapers.map((paper, index) => (
                <div 
                  key={index} 
                  className="p-4 bg-white border rounded-md shadow hover:shadow-md transition"
                >
                  <h3 className="font-semibold text-gray-900">{paper.title}</h3>
                  <div className="flex gap-2 mt-2">
                    <span className="inline-block bg-gray-100 rounded px-2 py-1 text-sm text-gray-600">
                      {paper.category}
                    </span>
                    <span className="inline-block bg-gray-100 rounded px-2 py-1 text-sm text-gray-600">
                      {paper.year}/{String(paper.month).padStart(2, '0')}
                    </span>
                  </div>
                  {/* <p className="mt-3 text-gray-700 text-sm">
                    {paper.summary}
                  </p> */}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Results Message */}
        {queryMode === 'filtering' && 
         !loading && 
         query && 
         filteredPapers.length === 0 && 
         !error && (
          <div className="text-center text-gray-600">
            No papers found matching your criteria
          </div>
        )}
      </div>
    </main>
  );
}