from fastai.vision import *


class Learner:
    def __init__(self, path, classes):
        self.model_classes = classes
        self.learner = load_learner(path)

    def predict(self, img_bytes, class_count):
        """
        Use the "FastAI"" API to predict the input image.
        The function will get the precision percent & label data for the X most accurate classes.

        :param byte[] img_bytes: Bytes of the input image
        :param int class_count: How many prediction classes should be returned
        :return: dictionary[] containing precision percent & label data ordered by accurate(First = highest)
        """
        img = open_image(BytesIO(img_bytes))
        aa, bb, preds = self.learner.predict(img)
        # Get all best predictions
        preds_sorted, idxs = preds.sort(descending=True)
        res = []
        for i in range(0, class_count):
            res.append({
                "sPercent": int(np.round(100 * preds_sorted[i].item(), 2)),
                "label":
                    self.model_classes[int(self.learner.data.classes[idxs[i]])]
            })
        return res

    def fetch_label(self, class_id):
        """
        Fetch label information for a specific class id.
        :param int class_id: ID of a class
        :return:
                -null if not class was found
                -Label object if a class was found.
        """
        if class_id > len(self.model_classes) or class_id < 0:
            return None
        return self.model_classes[class_id]
