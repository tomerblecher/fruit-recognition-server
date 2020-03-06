import os, glob
from fastai.vision import *
from fastai import *
from fastai.utils.show_install import *
from fastai.widgets import *


class Learner:
    def __init__(self, path , classes):
        self.model_classes = classes
        self.learner = load_learner(path)

    def predict(self, img_bytes):
        img = open_image(BytesIO(img_bytes))
        # img = open_image((img_bytes))
        _,_, preds = self.learner.predict(img)
        # Get all best predictions
        preds_sorted, idxs = preds.sort(descending=True)
        res = []
        for i in range(0,2):
            res.append({
                "sPercent": int(np.round(100 * preds_sorted[i].item(), 2)),
                "label":
                    self.model_classes[int(self.learner.data.classes[idxs[i]])]

            })

        # d = dict({self.learner.data.classes[i]: round(to_np(p) * 100, 2) for i, p in enumerate(outputs) if p > 0.2})
        return res
