import os
import warnings
from pathlib import Path

import joblib

warnings.filterwarnings("ignore")

BASEDIR = Path(__file__).resolve().parent


class WAF:
    def __init__(self, model=None, encoder=None) -> None:
        self._is_enabled = os.getenv("WAF_ENABLED", False)
        self.model = model
        self.encoder = encoder

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, status):
        self._is_enabled = status

    def check_artifacts(self):
        artifact_dir = BASEDIR / "artifacts"
        if artifact_dir.is_dir():
            print("dir found")
        else:
            print("No dir found")
        # artifact_dir.mkdir(exist_ok=True, parents=True)

    @classmethod
    def load_model(cls):
        model = joblib.load(BASEDIR / "artifacts" / "classifier.pkl")
        encoder = joblib.load(BASEDIR / "artifacts" / "vectorizer.pkl")
        return cls(model=model, encoder=encoder)

    def encode(self, query):

        return self.encoder.transform(query)

    @staticmethod
    def fix_proba(proba):
        p = proba[0]
        return p[1]

    def get_threat_probabilities(self, query):
        if isinstance(query, str):
            query = [query]

        vectorized_query = self.encode(query)

        proba = self.model.predict_proba(vectorized_query).round(4)

        return self.fix_proba(proba)


if __name__ == "__main__":

    # waf = WAF()
    # waf.is_enabled = True

    # if waf.is_enabled:
    #     waf.check_artifacts()

    model = WAF.load_model()

    prob = model.get_threat_probabilities(
        query="https://localhost:8080/?id=1/<script>asd</script>"
    )
    print(prob)
