import os
from pathlib import Path

import joblib

BASEDIR = Path().parent.parent


class WAF:
    def __init__(self) -> None:
        self._is_enabled = os.getenv("WAF_ENABLED", False)

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

    def load_model(self):
        model = joblib.load(BASEDIR / "artifacts" / "classifier.pkl")
        return model

    def encode(self, query):
        encoder = joblib.load(BASEDIR / "artifacts" / "vectorizer.pkl")
        vector = encoder.transform(query)
        return vector

    @staticmethod
    def fix_proba(proba):
        p = proba[0]
        return [["malicious_query_score", p[1]], ["normal_query_score", p[0]]]

    def get_threat_probabilities(self, query, model):
        if isinstance(query, str):
            query = [query]

        vectorized_query = self.encode(query)

        proba = model.predict_proba(vectorized_query).round(4)

        return self.fix_proba(proba)


if __name__ == "__main__":

    waf = WAF()
    waf.is_enabled = True

    if waf.is_enabled:
        waf.check_artifacts()

    model = waf.load_model()

    prob = waf.get_threat_probabilities(
        query="/?id=1/<script>asd</script>", model=model
    )
    print(prob)
