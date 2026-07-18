import numpy as np
import base64
import io
import os
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from torchvision import models, transforms
from PIL import Image
from ..config import settings

_retinal_model = None
_device = torch.device('cpu')

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])


def _build_model():
    try:
        import timm
    except ImportError:
        raise ImportError("timm is required for retinal model. Run: pip install timm")

    class HybridCNNViT(nn.Module):
        def __init__(self):
            super().__init__()
            resnet = models.resnet50(weights=None)
            self.cnn_branch = nn.Sequential(*list(resnet.children())[:-1])
            self.vit_branch = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=0)
            self.classifier = nn.Sequential(
                nn.Linear(2048+768, 512), nn.ReLU(), nn.Dropout(0.3),
                nn.Linear(512, 256),     nn.ReLU(), nn.Dropout(0.2),
                nn.Linear(256, 1),       nn.Sigmoid()
            )
        def forward(self, x):
            cnn_feat = self.cnn_branch(x).view(x.size(0), -1)
            vit_feat = self.vit_branch(x)
            return self.classifier(torch.cat([cnn_feat, vit_feat], dim=1)).squeeze(1)

    return HybridCNNViT()


def _load_retinal_model():
    global _retinal_model
    if _retinal_model is None:
        model_path = os.path.abspath(settings.RETINAL_MODEL_PATH)
        if not os.path.exists(model_path):
            return False
        _retinal_model = _build_model()
        _retinal_model.load_state_dict(torch.load(model_path, map_location=_device))
        _retinal_model.eval()
    return True


class GradCAM:
    def __init__(self, model):
        self.model        = model
        self.feature_maps = None
        self.gradients    = None
        self._hooks       = []
        target_layer = list(model.cnn_branch.children())[7]
        self._hooks.append(target_layer.register_forward_hook(
            lambda m, i, o: setattr(self, 'feature_maps', o)))
        self._hooks.append(target_layer.register_full_backward_hook(
            lambda m, gi, go: setattr(self, 'gradients', go[0])))

    def generate(self, inp):
        self.model.zero_grad()
        out = self.model(inp)
        out.backward()
        weights = self.gradients.mean(dim=[2, 3], keepdim=True)
        cam = torch.relu((weights * self.feature_maps).sum(dim=1, keepdim=True))
        cam = torch.nn.functional.interpolate(cam, size=(224, 224), mode='bilinear', align_corners=False)
        cam = cam.squeeze().cpu().detach().numpy()
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max - cam_min > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        return cam

    def remove(self):
        for h in self._hooks: h.remove()


def _overlay_to_base64(orig_np, heatmap):
    cmap     = matplotlib.colormaps['jet']   # compatible with matplotlib 3.7+
    heat_rgb = cmap(heatmap)[:, :, :3]
    overlay = np.clip((1-0.5)*orig_np + 0.5*heat_rgb, 0, 1)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(orig_np);   axes[0].set_title('Original');  axes[0].axis('off')
    axes[1].imshow(heatmap, cmap='jet'); axes[1].set_title('Heatmap'); axes[1].axis('off')
    axes[2].imshow(overlay);   axes[2].set_title('Overlay');   axes[2].axis('off')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def predict_retinal(image_bytes: bytes) -> dict:
    """Predict retinal risk and generate Grad-CAM. Returns risk_score, gradcam_b64."""
    if not _load_retinal_model():
        return {"risk_score": None, "gradcam": None, "error": "Retinal model not available"}

    # Load and preprocess image
    img_pil  = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    orig_np  = np.array(img_pil.resize((224, 224))).astype(np.float32) / 255.0
    inp      = val_transform(img_pil).unsqueeze(0).to(_device)
    inp.requires_grad_(True)

    # Prediction
    with torch.no_grad():
        prob = float(_retinal_model(inp.detach()).item())

    # Grad-CAM
    gradcam     = GradCAM(_retinal_model)
    inp_grad    = val_transform(img_pil).unsqueeze(0).to(_device).requires_grad_(True)
    heatmap     = gradcam.generate(inp_grad)
    gradcam_b64 = _overlay_to_base64(orig_np, heatmap)
    gradcam.remove()

    return {
        "risk_score": round(prob * 100, 2),
        "gradcam":    gradcam_b64,
    }
