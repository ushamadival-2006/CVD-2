import React from 'react';

interface Props { score: number; level: string; confidence: string; source: string; }

export default function RiskGauge({ score, level, confidence, source }: Props) {
  const clamp   = Math.min(100, Math.max(0, score));
  const angle   = -90 + (clamp / 100) * 180;
  const color   = clamp >= 70 ? '#dc2626' : clamp >= 30 ? '#d97706' : '#16a34a';
  const bgColor = clamp >= 70 ? 'bg-red-50 border-red-200'
                : clamp >= 30 ? 'bg-amber-50 border-amber-200'
                : 'bg-green-50 border-green-200';

  // SVG arc helpers
  const cx = 110, cy = 110, r = 80;
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const arcX  = (deg: number) => cx + r * Math.cos(toRad(deg));
  const arcY  = (deg: number) => cy + r * Math.sin(toRad(deg));

  const lowEnd  = arcX(-30); const lowEndY  = arcY(-30);
  const midEnd  = arcX(30);  const midEndY  = arcY(30);
  const highEnd = arcX(90);  const highEndY = arcY(90);

  const needleX = cx + (r - 10) * Math.cos(toRad(angle - 90));
  const needleY = cy + (r - 10) * Math.sin(toRad(angle - 90));

  return (
    <div className={`rounded-2xl border-2 p-6 text-center ${bgColor}`}>
      <svg viewBox="0 0 220 130" className="w-64 mx-auto">
        {/* Background arcs */}
        <path d={`M ${arcX(-90)} ${arcY(-90)} A ${r} ${r} 0 0 1 ${arcX(-30)} ${arcY(-30)}`}
          fill="none" stroke="#16a34a" strokeWidth="16" strokeLinecap="round" />
        <path d={`M ${arcX(-30)} ${arcY(-30)} A ${r} ${r} 0 0 1 ${arcX(30)} ${arcY(30)}`}
          fill="none" stroke="#d97706" strokeWidth="16" strokeLinecap="round" />
        <path d={`M ${arcX(30)} ${arcY(30)} A ${r} ${r} 0 0 1 ${arcX(90)} ${arcY(90)}`}
          fill="none" stroke="#dc2626" strokeWidth="16" strokeLinecap="round" />
        {/* Needle */}
        <line x1={cx} y1={cy} x2={needleX} y2={needleY}
          stroke="#1f2937" strokeWidth="3" strokeLinecap="round" />
        <circle cx={cx} cy={cy} r="5" fill="#1f2937" />
        {/* Score text */}
        <text x={cx} y={cy + 22} textAnchor="middle" fontSize="18" fontWeight="bold" fill={color}>
          {clamp.toFixed(1)}%
        </text>
        {/* Labels */}
        <text x="28"  y="115" fontSize="9" fill="#16a34a" textAnchor="middle">LOW</text>
        <text x="110" y="118" fontSize="9" fill="#d97706" textAnchor="middle">INTER.</text>
        <text x="192" y="115" fontSize="9" fill="#dc2626" textAnchor="middle">HIGH</text>
      </svg>

      <div className="mt-2 space-y-1">
        <p className="text-2xl font-bold" style={{ color }}>{level}</p>
        <div className="flex justify-center gap-4 text-sm text-gray-600">
          <span>Confidence: <strong>{confidence}</strong></span>
          <span>Source: <strong>{source}</strong></span>
        </div>
      </div>
    </div>
  );
}
