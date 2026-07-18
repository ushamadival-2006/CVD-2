import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer } from 'recharts';

interface Props { shap: Record<string, number>; }

export default function SHAPChart({ shap }: Props) {
  const sorted = Object.entries(shap)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 12)
    .map(([name, value]) => ({
      name: name.replace(/_/g, ' ').replace(/ Encoded$/, ''),
      value: parseFloat(value.toFixed(4)),
    }))
    .reverse();

  return (
    <div>
      <h3 className="font-semibold text-gray-800 mb-3">Feature Importance (SHAP)</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={sorted} layout="vertical" margin={{ left: 10, right: 20, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" tickFormatter={(v) => v.toFixed(3)} fontSize={11} />
          <YAxis type="category" dataKey="name" width={150} fontSize={11} />
          <Tooltip formatter={(v: number) => v.toFixed(4)} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {sorted.map((entry, i) => (
              <Cell key={i} fill={entry.value >= 0 ? '#dc2626' : '#2563eb'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-500 mt-2">
        Red = increases risk · Blue = decreases risk
      </p>
    </div>
  );
}
