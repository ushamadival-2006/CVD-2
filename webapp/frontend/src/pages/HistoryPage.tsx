import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter } from 'lucide-react';
import { predictApi } from '../api/client';
import { HistoryItem } from '../types';

function riskBadge(level: string) {
  if (level.includes('HIGH'))  return 'bg-red-100 text-red-700';
  if (level.includes('LOW'))   return 'bg-green-100 text-green-700';
  return 'bg-amber-100 text-amber-700';
}

const PAGE_SIZE = 10;

export default function HistoryPage() {
  const [history, setHistory]   = useState<HistoryItem[]>([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState('');
  const [filter, setFilter]     = useState('All');
  const [page, setPage]         = useState(1);

  useEffect(() => {
    predictApi.history()
      .then((res) => setHistory(res.data))
      .finally(() => setLoading(false));
  }, []);

  const filtered = history.filter((h) => {
    const matchSearch = !search ||
      h.patient_name?.toLowerCase().includes(search.toLowerCase()) ||
      h.risk_level.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'All' || h.risk_level.includes(filter);
    return matchSearch && matchFilter;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paged      = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Assessment History</h1>
        <p className="text-gray-500 text-sm mt-1">All your past CVD risk predictions</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-5">
        <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2 bg-white flex-1 max-w-xs">
          <Search size={16} className="text-gray-400" />
          <input
            type="text" placeholder="Search patient or level…"
            value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="text-sm outline-none w-full"
          />
        </div>
        <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2 bg-white">
          <Filter size={16} className="text-gray-400" />
          <select value={filter} onChange={(e) => { setFilter(e.target.value); setPage(1); }}
            className="text-sm outline-none bg-transparent">
            <option value="All">All Levels</option>
            <option value="HIGH">High Risk</option>
            <option value="INTERMEDIARY">Intermediary</option>
            <option value="LOW">Low Risk</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
        {loading ? (
          <div className="p-12 text-center text-gray-400">Loading…</div>
        ) : paged.length === 0 ? (
          <div className="p-12 text-center text-gray-400">No results found.</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wider text-gray-500 bg-gray-50">
                    <th className="px-6 py-3">#</th>
                    <th className="px-6 py-3">Date</th>
                    <th className="px-6 py-3">Patient</th>
                    <th className="px-6 py-3">Risk Score</th>
                    <th className="px-6 py-3">Level</th>
                    <th className="px-6 py-3">Source</th>
                    <th className="px-6 py-3">Confidence</th>
                    <th className="px-6 py-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {paged.map((item, idx) => (
                    <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-3 text-gray-400">{(page-1)*PAGE_SIZE + idx + 1}</td>
                      <td className="px-6 py-3 text-gray-600">{new Date(item.created_at).toLocaleDateString()}</td>
                      <td className="px-6 py-3 font-medium">{item.patient_name || '—'}</td>
                      <td className="px-6 py-3 font-bold">{item.risk_score.toFixed(1)}%</td>
                      <td className="px-6 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${riskBadge(item.risk_level)}`}>
                          {item.risk_level}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-gray-500">{item.source}</td>
                      <td className="px-6 py-3 text-gray-500">{item.confidence}</td>
                      <td className="px-6 py-3">
                        <Link to={`/result/${item.id}`}
                          className="text-blue-600 hover:underline text-xs font-medium">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-6 py-3 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Showing {(page-1)*PAGE_SIZE+1}–{Math.min(page*PAGE_SIZE, filtered.length)} of {filtered.length}
              </p>
              <div className="flex gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                  <button key={p} onClick={() => setPage(p)}
                    className={`w-7 h-7 rounded text-xs font-medium transition-colors
                      ${p === page ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
