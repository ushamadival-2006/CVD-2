import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Download, PlusCircle, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import { predictApi } from '../api/client';
import { PredictionResponse } from '../types';
import RiskGauge from '../components/RiskGauge';
import SHAPChart from '../components/SHAPChart';
import GradCAMImage from '../components/GradCAMImage';
import RecommendationCards from '../components/RecommendationCards';
import RiskExplanation from '../components/RiskExplanation';

export default function ResultPage() {
  const { id }    = useParams<{ id: string }>();
  const [result, setResult]   = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // First check sessionStorage (fresh result)
    const cached = sessionStorage.getItem('lastResult');
    const cachedId = sessionStorage.getItem('lastResultId');
    if (cached && cachedId === id) {
      setResult(JSON.parse(cached));
      setLoading(false);
      return;
    }
    // Otherwise fetch from API by numeric id
    if (id && !isNaN(Number(id))) {
      predictApi.getById(Number(id))
        .then((res) => setResult(res.data))
        .catch(() => toast.error('Could not load result'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [id]);

  const downloadPDF = () => {
    if (!result) return;
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text('CVD Risk Assessment Report', 20, 20);
    doc.setFontSize(12);
    doc.text(`Date: ${new Date(result.timestamp).toLocaleString()}`, 20, 32);
    doc.text(`Risk Score: ${result.risk_score.toFixed(1)}%`, 20, 42);
    doc.text(`Risk Level: ${result.risk_level}`, 20, 52);
    doc.text(`Confidence: ${result.confidence}`, 20, 62);
    doc.text(`Source: ${result.source}`, 20, 72);
    doc.setFontSize(13);
    doc.text('Recommendations', 20, 88);
    doc.setFontSize(11);
    const recs = result.recommendations;
    const dietLines  = doc.splitTextToSize(`Diet: ${recs.diet}`, 170);
    const exLines    = doc.splitTextToSize(`Exercise: ${recs.exercise}`, 170);
    const medLines   = doc.splitTextToSize(`Medical: ${recs.medical_guidance}`, 170);
    let yPos = 98;
    if (result.risk_explanation) {
      doc.setFontSize(13);
      doc.text('Why This Risk Score?', 20, 82);
      doc.setFontSize(10);
      const expLines = doc.splitTextToSize(result.risk_explanation, 170);
      doc.text(expLines, 20, 90);
      yPos = 90 + expLines.length * 5 + 10;
      doc.setFontSize(13);
      doc.text('Recommendations', 20, yPos);
      yPos += 10;
    }
    doc.setFontSize(11);
    doc.text(dietLines, 20, yPos);
    doc.text(exLines,  20, yPos + dietLines.length * 6);
    doc.text(medLines, 20, yPos + (dietLines.length + exLines.length) * 6);
    doc.save(`cvd_risk_report_${id}.pdf`);
    toast.success('PDF downloaded');
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
    </div>
  );

  if (!result) return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      <p className="text-gray-500 mb-4">Result not found.</p>
      <Link to="/dashboard" className="text-blue-600 hover:underline">← Back to Dashboard</Link>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link to="/dashboard" className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2">
            <ArrowLeft size={16} /> Back
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Risk Assessment Results</h1>
          <p className="text-gray-500 text-sm">{new Date(result.timestamp).toLocaleString()}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={downloadPDF}
            className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors">
            <Download size={16} /> PDF Report
          </button>
          <Link to="/assessment"
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors">
            <PlusCircle size={16} /> New
          </Link>
        </div>
      </div>

      {/* Risk Gauge */}
      <div className="flex justify-center mb-6">
        <div className="w-full max-w-sm">
          <RiskGauge
            score={result.risk_score}
            level={result.risk_level}
            confidence={result.confidence}
            source={result.source}
          />
        </div>
      </div>

      {/* LLM Risk Explanation — why this score? */}
      {result.risk_explanation && (
        <div className="mb-8">
          <RiskExplanation
            explanation={result.risk_explanation}
            riskLevel={result.risk_level}
          />
        </div>
      )}

      {/* SHAP + Grad-CAM Explanation */}
      {(result.explanation.shap || result.explanation.gradcam) && (
        <div className="mb-2">
          <h2 className="font-semibold text-gray-800 text-lg mb-4">AI Model Explanation</h2>
        </div>
      )}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {result.explanation.shap && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
            <SHAPChart shap={result.explanation.shap} />
          </div>
        )}
        {result.explanation.gradcam && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
            <GradCAMImage gradcam={result.explanation.gradcam} label="Left Eye Grad-CAM" />
          </div>
        )}
        {(result.explanation as any).gradcam_right && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
            <GradCAMImage gradcam={(result.explanation as any).gradcam_right} label="Right Eye Grad-CAM" />
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <h2 className="font-semibold text-gray-800 mb-4 text-lg">Personalised Recommendations</h2>
        <RecommendationCards
          diet={result.recommendations.diet}
          exercise={result.recommendations.exercise}
          medical_guidance={result.recommendations.medical_guidance}
          powered_by={(result.recommendations as any).powered_by}
        />
      </div>
    </div>
  );
}
