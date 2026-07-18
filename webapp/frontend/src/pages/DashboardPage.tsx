import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, TrendingUp, AlertTriangle, Clock, PlusCircle, History } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { predictApi } from '../api/client';
import { HistoryItem } from '../types';

function riskColor(level: string) {
  if (level.includes('HIGH'))  return 'text-red-600 bg-red-50';
  if (level.includes('LOW'))   return 'text-green-600 bg-green-50';
  return 'text-amber-600 bg-amber-50';
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    predictApi.history().then((res) => setHistory(res.data)).finally(() => setLoading(false));
  }, []);

  const highCount = history.filter(h => h.risk_level.includes('HIGH')).length;
  const lastDate  = history.length ? new Date(history[0].created_at).toLocaleDateString() : '—';
  const recent    = history.slice(0, 5);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.name?.split(' ')[0]}! 👋
        </h1>
        <p className="text-gray-500 mt-1">Monitor and manage your cardiovascular health</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {[
          { icon: <Activity size={22} className="text-blue-600" />, label: 'Total Assessments', value: history.length, bg: 'bg-blue-50' },
          { icon: <AlertTriangle size={22} className="text-red-600" />, label: 'High Risk', value: highCount, bg: 'bg-red-50' },
          { icon: <Clock size={22} className="text-green-600" />, label: 'Last Assessment', value: lastDate, bg: 'bg-green-50' },
        ].map(({ icon, label, value, bg }) => (
          <div key={label} className={`${bg} rounded-xl p-5 flex items-center gap-4`}>
            <div className="bg-white rounded-lg p-2 shadow-sm">{icon}</div>
            <div>
              <p className="text-sm text-gray-600">{label}</p>
              <p className="text-xl font-bold text-gray-900">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* CTA Buttons */}
      <div className="flex flex-wrap gap-3 mb-8">
        <Link to="/assessment"
          className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors">
          <PlusCircle size={18} /> Start New Assessment
        </Link>
        <Link to="/history"
          className="flex items-center gap-2 border border-gray-300 text-gray-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-gray-50 transition-colors">
          <History size={18} /> View Full History
        </Link>
      </div>

      {/* Recent Predictions */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800">Recent Assessments</h2>
        </div>
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading…</div>
        ) : recent.length === 0 ? (
          <div className="p-8 text-center">
            <TrendingUp size={40} className="text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">No assessments yet.</p>
            <Link to="/assessment" className="text-blue-600 text-sm hover:underline">
              Start your first assessment →
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 text-xs uppercase tracking-wider bg-gray-50">
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3">Patient</th>
                  <th className="px-6 py-3">Risk Score</th>
                  <th className="px-6 py-3">Risk Level</th>
                  <th className="px-6 py-3">Source</th>
                  <th className="px-6 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {recent.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-3 text-gray-600">{new Date(item.created_at).toLocaleDateString()}</td>
                    <td className="px-6 py-3 font-medium">{item.patient_name || '—'}</td>
                    <td className="px-6 py-3 font-bold">{item.risk_score.toFixed(1)}%</td>
                    <td className="px-6 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${riskColor(item.risk_level)}`}>
                        {item.risk_level}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-gray-500">{item.source}</td>
                    <td className="px-6 py-3">
                      <Link to={`/result/${item.id}`} className="text-blue-600 hover:underline text-xs font-medium">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
