import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface Props {
  gradcam: string;
  label?: string;
}

export default function GradCAMImage({ gradcam, label = 'Grad-CAM Heatmap' }: Props) {
  const [show, setShow] = useState(true);

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800">{label}</h3>
        <button onClick={() => setShow(!show)}
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
          {show ? <EyeOff size={16} /> : <Eye size={16} />}
          {show ? 'Hide' : 'Show'}
        </button>
      </div>
      {show && (
        <div>
          <img
            src={`data:image/png;base64,${gradcam}`}
            alt={label}
            className="w-full rounded-lg border border-gray-200"
          />
          <p className="text-xs text-gray-500 mt-2">
            Warm colours (red/yellow) highlight regions that most influenced the retinal prediction.
          </p>
        </div>
      )}
    </div>
  );
}
