import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Upload, X, ChevronRight, Eye } from 'lucide-react';
import { predictApi } from '../api/client';
import { ClinicalFormData } from '../types';

const Field = ({ label, error, children, required = true }: any) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1">
      {label}{required && <span className="text-red-500 ml-0.5">*</span>}
    </label>
    {children}
    {error && <p className="text-red-500 text-xs mt-1">{error.message}</p>}
  </div>
);

interface EyeUploadProps {
  label: string;
  file: File | null;
  preview: string | null;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onClear: () => void;
}

function EyeUpload({ label, file, preview, onChange, onClear }: EyeUploadProps) {
  return (
    <div>
      <p className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
        <Eye size={15} className="text-blue-500" /> {label}
        <span className="text-xs text-gray-400 font-normal">(optional)</span>
      </p>
      {preview ? (
        <div className="relative inline-block">
          <img src={preview} alt={label} className="max-h-40 rounded-lg border border-gray-200 w-full object-cover" />
          <button type="button" onClick={onClear}
            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-0.5 hover:bg-red-600">
            <X size={14} />
          </button>
          <p className="text-xs text-gray-500 mt-1 truncate">{file?.name}</p>
        </div>
      ) : (
        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors">
          <Upload size={20} className="text-gray-400 mb-1" />
          <span className="text-xs text-gray-500">Click to upload</span>
          <span className="text-xs text-gray-400">PNG, JPG, JPEG • Max 10 MB</span>
          <input type="file" accept="image/png,image/jpeg,image/jpg" className="hidden" onChange={onChange} />
        </label>
      )}
    </div>
  );
}

export default function AssessmentPage() {
  const navigate  = useNavigate();
  const [loading, setLoading]   = useState(false);
  const [hasRetinal, setHasRetinal] = useState(false);

  // Left eye
  const [leftFile, setLeftFile]     = useState<File | null>(null);
  const [leftPreview, setLeftPreview] = useState<string | null>(null);

  // Right eye
  const [rightFile, setRightFile]     = useState<File | null>(null);
  const [rightPreview, setRightPreview] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<ClinicalFormData & { patient_name?: string }>();

  const handleEyeChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    setFile: (f: File | null) => void,
    setPreview: (s: string | null) => void
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) { toast.error('Image must be ≤ 10 MB'); return; }
    setFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const clearRetinal = () => {
    setLeftFile(null);  setLeftPreview(null);
    setRightFile(null); setRightPreview(null);
  };

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      const fd = new FormData();
      // Append clinical fields
      Object.entries(data).forEach(([k, v]) => {
        if (v !== undefined && v !== '') fd.append(k, String(v));
      });
      // Append eye images with the correct field names the backend expects
      if (hasRetinal) {
        if (leftFile)  fd.append('left_eye_image',  leftFile,  leftFile.name);
        if (rightFile) fd.append('right_eye_image', rightFile, rightFile.name);
      }

      const res = await predictApi.fusion(fd);
      sessionStorage.setItem('lastResult', JSON.stringify(res.data));
      sessionStorage.setItem('lastResultId', res.data.patient_id);
      toast.success('Assessment complete!');
      navigate(`/result/${res.data.patient_id}`);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Assessment failed. Please try again.');
    } finally { setLoading(false); }
  };

  const inputCls  = "w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";
  const selectCls = inputCls + " bg-white";

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">New Risk Assessment</h1>
        <p className="text-gray-500 text-sm mt-1">
          Fields marked with <span className="text-red-500">*</span> are required
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

        {/* ── Clinical Data ──────────────────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-5 flex items-center gap-2">
            <span className="w-6 h-6 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center font-bold">1</span>
            Clinical Data
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label="Patient Name" error={errors.patient_name} required={false}>
              <input {...register('patient_name')} placeholder="Optional" className={inputCls} />
            </Field>
            <Field label="Age (years)" error={errors.age}>
              <input type="number" {...register('age', { required: 'Required', min: { value: 18, message: 'Min 18' }, max: { value: 120, message: 'Max 120' } })} placeholder="45" className={inputCls} />
            </Field>
            <Field label="Gender" error={errors.gender}>
              <select {...register('gender', { required: 'Required' })} className={selectCls}>
                <option value="">Select…</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </Field>
            <Field label="Height (cm)" error={errors.height_cm}>
              <input type="number" {...register('height_cm', { required: 'Required', min: { value: 100, message: 'Min 100cm' }, max: { value: 250, message: 'Max 250cm' } })} placeholder="175" className={inputCls} />
            </Field>
            <Field label="Weight (kg)" error={errors.weight_kg}>
              <input type="number" {...register('weight_kg', { required: 'Required', min: { value: 30, message: 'Min 30' }, max: { value: 300, message: 'Max 300' } })} placeholder="80" className={inputCls} />
            </Field>
            <Field label="Systolic BP (mmHg)" error={errors.systolic_bp}>
              <input type="number" {...register('systolic_bp', { required: 'Required', min: { value: 70, message: 'Min 70' }, max: { value: 250, message: 'Max 250' } })} placeholder="130" className={inputCls} />
            </Field>
            <Field label="Diastolic BP (mmHg)" error={errors.diastolic_bp}>
              <input type="number" {...register('diastolic_bp', { required: 'Required', min: { value: 40, message: 'Min 40' }, max: { value: 150, message: 'Max 150' } })} placeholder="85" className={inputCls} />
            </Field>
            <Field label="Total Cholesterol (mg/dL)" error={errors.total_cholesterol}>
              <input type="number" {...register('total_cholesterol', { required: 'Required', min: { value: 50, message: 'Min 50' }, max: { value: 500, message: 'Max 500' } })} placeholder="210" className={inputCls} />
            </Field>
            <Field label="HDL (mg/dL)" error={errors.hdl}>
              <input type="number" {...register('hdl', { required: 'Required', min: { value: 10, message: 'Min 10' }, max: { value: 200, message: 'Max 200' } })} placeholder="45" className={inputCls} />
            </Field>
            <Field label="Fasting Blood Sugar (mg/dL)" error={errors.fasting_blood_sugar}>
              <input type="number" {...register('fasting_blood_sugar', { required: 'Required', min: { value: 50, message: 'Min 50' }, max: { value: 600, message: 'Max 600' } })} placeholder="110" className={inputCls} />
            </Field>
            <Field label="Smoking Status" error={errors.smoking_status}>
              <select {...register('smoking_status', { required: 'Required' })} className={selectCls}>
                <option value="">Select…</option>
                <option value="Y">Yes</option>
                <option value="N">No</option>
              </select>
            </Field>
            <Field label="Diabetes Status" error={errors.diabetes_status}>
              <select {...register('diabetes_status', { required: 'Required' })} className={selectCls}>
                <option value="">Select…</option>
                <option value="Y">Yes</option>
                <option value="N">No</option>
              </select>
            </Field>
            <Field label="Physical Activity Level" error={errors.physical_activity}>
              <select {...register('physical_activity', { required: 'Required' })} className={selectCls}>
                <option value="">Select…</option>
                <option value="Low">Low</option>
                <option value="Moderate">Moderate</option>
                <option value="High">High</option>
              </select>
            </Field>
            <Field label="Family History of CVD" error={errors.family_history_cvd}>
              <select {...register('family_history_cvd', { required: 'Required' })} className={selectCls}>
                <option value="">Select…</option>
                <option value="Y">Yes</option>
                <option value="N">No</option>
              </select>
            </Field>
          </div>
        </div>

        {/* ── Retinal Images ─────────────────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-1 flex items-center gap-2">
            <span className="w-6 h-6 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center font-bold">2</span>
            Retinal Fundus Images
            <span className="text-xs font-normal text-gray-400">(Optional)</span>
          </h2>
          <p className="text-xs text-gray-500 mb-4 ml-8">
            Upload one or both eyes. If both are provided, the AI averages both scores for better accuracy.
          </p>

          {/* Yes / No toggle */}
          <div className="flex gap-3 mb-5">
            {[true, false].map((val) => (
              <button key={String(val)} type="button"
                onClick={() => { setHasRetinal(val); if (!val) clearRetinal(); }}
                className={`px-5 py-2 rounded-lg text-sm font-medium border transition-colors
                  ${hasRetinal === val
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}>
                {val ? 'Yes, I have fundus images' : 'No'}
              </button>
            ))}
          </div>

          {hasRetinal && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <EyeUpload
                label="Left Eye"
                file={leftFile}
                preview={leftPreview}
                onChange={(e) => handleEyeChange(e, setLeftFile, setLeftPreview)}
                onClear={() => { setLeftFile(null); setLeftPreview(null); }}
              />
              <EyeUpload
                label="Right Eye"
                file={rightFile}
                preview={rightPreview}
                onChange={(e) => handleEyeChange(e, setRightFile, setRightPreview)}
                onClear={() => { setRightFile(null); setRightPreview(null); }}
              />
            </div>
          )}

          {hasRetinal && !leftFile && !rightFile && (
            <p className="text-amber-600 text-xs mt-3">
              ⚠️ Please upload at least one eye image, or select "No" to proceed with clinical data only.
            </p>
          )}
        </div>

        {/* ── Submit ─────────────────────────────────────────────────────── */}
        <div className="flex gap-3">
          <button type="submit" disabled={loading || (hasRetinal && !leftFile && !rightFile)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-xl transition-colors disabled:opacity-60">
            {loading
              ? (<><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1" />Analysing…</>)
              : (<>Get Results <ChevronRight size={18} /></>)
            }
          </button>
          <button type="button"
            onClick={() => { clearRetinal(); setHasRetinal(false); }}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors">
            Clear
          </button>
        </div>
      </form>
    </div>
  );
}
