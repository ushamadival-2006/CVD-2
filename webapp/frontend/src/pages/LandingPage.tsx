import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, Shield, Brain, FileText, ArrowRight } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex bg-white/20 text-white px-4 py-1.5 rounded-full text-sm font-medium mb-6">
            AI-Powered Cardiovascular Risk Prediction
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-5 leading-tight">
            Know Your Heart Health<br />
            <span className="text-blue-200">Before It's Too Late</span>
          </h1>
          <p className="text-blue-100 text-lg mb-8 max-w-2xl mx-auto">
            CVDRisk combines clinical data and retinal imaging with advanced AI to assess your
            cardiovascular disease risk with clinical-grade accuracy.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/signup"
              className="flex items-center gap-2 bg-white text-blue-700 px-7 py-3 rounded-xl font-semibold hover:bg-blue-50 transition-colors">
              Check Your CVD Risk <ArrowRight size={18} />
            </Link>
            <Link to="/login"
              className="flex items-center gap-2 border border-white/40 text-white px-7 py-3 rounded-xl font-semibold hover:bg-white/10 transition-colors">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
            <p className="text-gray-500 mt-3">Three steps to understand your cardiovascular health</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: <FileText size={28} className="text-blue-600" />, step: '01',
                title: 'Enter Clinical Data', desc: 'Fill in your age, blood pressure, cholesterol, and other key clinical markers.' },
              { icon: <Activity size={28} className="text-purple-600" />, step: '02',
                title: 'Upload Retinal Image', desc: 'Optionally upload a fundus photograph. Our hybrid AI extracts vascular features invisible to the naked eye.' },
              { icon: <Brain size={28} className="text-green-600" />, step: '03',
                title: 'Get AI Analysis', desc: 'Receive a personalised risk score, SHAP explanations, Grad-CAM heatmaps, and actionable recommendations.' },
            ].map(({ icon, step, title, desc }) => (
              <div key={title} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <div className="text-xs font-bold text-gray-400 mb-3">STEP {step}</div>
                <div className="mb-3">{icon}</div>
                <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-500 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            { label: 'Clinical Accuracy', value: '81.3%' },
            { label: 'Retinal AUC', value: '82.9%' },
            { label: 'Fusion Accuracy', value: '~85%' },
            { label: 'Patients Analysed', value: '4,400+' },
          ].map(({ label, value }) => (
            <div key={label}>
              <div className="text-3xl font-bold text-blue-600">{value}</div>
              <div className="text-sm text-gray-500 mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 bg-blue-600 text-white text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to assess your heart health?</h2>
        <p className="text-blue-200 mb-7 max-w-xl mx-auto">
          It takes less than 5 minutes. Get your personalised CVD risk score and evidence-based recommendations.
        </p>
        <Link to="/signup"
          className="inline-flex items-center gap-2 bg-white text-blue-700 px-8 py-3.5 rounded-xl font-semibold hover:bg-blue-50 transition-colors">
          Get Started Free <ArrowRight size={18} />
        </Link>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8 px-4 text-center text-sm">
        <div className="flex items-center justify-center gap-2 text-white mb-2">
          <Activity size={18} className="text-blue-400" />
          <span className="font-bold">CVDRisk</span>
        </div>
        <p>For research and informational purposes only. Not a substitute for professional medical advice.</p>
        <p className="mt-1">© {new Date().getFullYear()} CVDRisk AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
