from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from math import exp

import numpy as np


@dataclass(frozen=True)
class MachineSnapshot:
    machine_id: str
    as_of_date: date
    rolling_downtime_variance: float
    anomaly_frequency: float
    output_degradation_trend: float
    scrap_variance: float
    downtime_trend: float
    scrap_trend: float
    shift_scrap_correlation: float
    health_score: float
    data_points: int


@dataclass(frozen=True)
class DriftSignal:
    machine_id: str
    concept_drift_score: float
    concept_drift_detected: bool
    baseline_deviation_detected: bool
    change_point_detected: bool
    change_point_date: date | None


@dataclass(frozen=True)
class MonitoringSnapshot:
    model_accuracy: float
    brier_score: float
    tracked_drift_machines: int
    retrain_recommended_on: date
    last_trained_on: date


@dataclass(frozen=True)
class MachineRisk:
    machine_id: str
    failure_probability_next_7_days: float
    confidence_score: float


@dataclass
class TrainingData:
    machine_ids: list[str]
    X: np.ndarray
    y: np.ndarray


class LogisticRegressionLite:
    def __init__(self, learning_rate: float = 0.08, epochs: int = 500, l2: float = 0.01) -> None:
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.l2 = l2
        self.weights: np.ndarray | None = None
        self.bias: float = 0.0

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -40.0, 40.0)
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, X: np.ndarray, y: np.ndarray, reset: bool = True) -> None:
        if X.size == 0 or y.size == 0:
            return
        n_samples, n_features = X.shape
        if reset or self.weights is None or self.weights.shape[0] != n_features:
            self.weights = np.zeros(n_features, dtype=float)
            self.bias = 0.0

        for _ in range(self.epochs):
            linear = X @ self.weights + self.bias
            preds = self._sigmoid(linear)
            error = preds - y
            dw = (X.T @ error) / n_samples + self.l2 * self.weights
            db = float(np.mean(error))
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if X.size == 0:
            return np.array([], dtype=float)
        if self.weights is None:
            return np.full((X.shape[0],), 0.5, dtype=float)
        linear = X @ self.weights + self.bias
        return self._sigmoid(linear)


class PredictiveIntelligenceEngine:
    DOWNTIME_WEIGHT = 0.35
    ANOMALY_WEIGHT = 0.25
    OUTPUT_WEIGHT = 0.25
    SCRAP_WEIGHT = 0.15

    def __init__(self) -> None:
        self.model = LogisticRegressionLite()
        self.feature_mean: np.ndarray | None = None
        self.feature_std: np.ndarray | None = None
        self.last_trained_on: date | None = None

    @staticmethod
    def _safe_ratio(num: float, den: float) -> float:
        if den == 0:
            return 0.0
        return num / den

    @staticmethod
    def _slope(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values), dtype=float)
        y = np.array(values, dtype=float)
        x_center = x - np.mean(x)
        y_center = y - np.mean(y)
        den = float(np.sum(x_center**2))
        if den == 0:
            return 0.0
        return float(np.sum(x_center * y_center) / den)

    @staticmethod
    def _normalized_variance(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean_value = float(np.mean(values))
        variance = float(np.var(values))
        return min(1.0, variance / ((abs(mean_value) + 1.0) ** 2))

    def _build_snapshot(
        self,
        machine_id: str,
        as_of_date: date,
        history: list[dict],
        shift_scrap_correlation: float,
    ) -> MachineSnapshot:
        downtime_series = [float(r["downtime_minutes"]) for r in history]
        output_series = [float(r["output_units"]) for r in history]
        scrap_series = [float(r["scrap_units"]) for r in history]

        rolling_window = history[-14:] if len(history) >= 14 else history
        rolling_downtime = [float(r["downtime_minutes"]) for r in rolling_window]
        rolling_scrap = [float(r["scrap_units"]) for r in rolling_window]
        rolling_output = [float(r["output_units"]) for r in rolling_window]

        downtime_variance = self._normalized_variance(rolling_downtime)
        scrap_variance = self._normalized_variance(rolling_scrap)

        output_slope = self._slope(rolling_output)
        output_mean = abs(float(np.mean(rolling_output))) if rolling_output else 1.0
        output_degradation = min(1.0, max(0.0, -self._safe_ratio(output_slope, output_mean)))

        downtime_mu = float(np.mean(downtime_series)) if downtime_series else 0.0
        downtime_sigma = float(np.std(downtime_series)) if downtime_series else 0.0
        scrap_mu = float(np.mean(scrap_series)) if scrap_series else 0.0
        scrap_sigma = float(np.std(scrap_series)) if scrap_series else 0.0

        anomaly_hits = 0
        for row in rolling_window:
            downtime = float(row["downtime_minutes"])
            scrap = float(row["scrap_units"])
            downtime_z = 0.0 if downtime_sigma == 0 else abs((downtime - downtime_mu) / downtime_sigma)
            scrap_z = 0.0 if scrap_sigma == 0 else abs((scrap - scrap_mu) / scrap_sigma)
            if downtime_z >= 2.0 or scrap_z >= 2.0:
                anomaly_hits += 1
        anomaly_frequency = self._safe_ratio(anomaly_hits, max(len(rolling_window), 1))

        health_score = (
            self.DOWNTIME_WEIGHT * downtime_variance
            + self.ANOMALY_WEIGHT * anomaly_frequency
            + self.OUTPUT_WEIGHT * output_degradation
            + self.SCRAP_WEIGHT * scrap_variance
        ) * 100.0

        return MachineSnapshot(
            machine_id=machine_id,
            as_of_date=as_of_date,
            rolling_downtime_variance=round(downtime_variance, 4),
            anomaly_frequency=round(anomaly_frequency, 4),
            output_degradation_trend=round(output_degradation, 4),
            scrap_variance=round(scrap_variance, 4),
            downtime_trend=round(max(0.0, self._slope(rolling_downtime)), 4),
            scrap_trend=round(max(0.0, self._slope(rolling_scrap)), 4),
            shift_scrap_correlation=round(shift_scrap_correlation, 4),
            health_score=round(max(0.0, min(100.0, health_score)), 2),
            data_points=len(history),
        )

    @staticmethod
    def _group_by_machine(rows: list[dict]) -> dict[str, list[dict]]:
        grouped: dict[str, list[dict]] = {}
        for row in rows:
            grouped.setdefault(str(row["machine_id"]), []).append(row)
        for machine_rows in grouped.values():
            machine_rows.sort(key=lambda r: r["date"])
        return grouped

    @staticmethod
    def _shift_scrap_correlation(shift_rows: list[dict]) -> dict[str, float]:
        grouped: dict[str, dict[str, list[float]]] = {}
        for row in shift_rows:
            machine_id = str(row["machine_id"])
            shift = str(row["shift"])
            grouped.setdefault(machine_id, {}).setdefault(shift, []).append(float(row["scrap_percent"]))

        correlation: dict[str, float] = {}
        for machine_id, shift_map in grouped.items():
            shift_means = [float(np.mean(values)) for values in shift_map.values() if values]
            if not shift_means:
                correlation[machine_id] = 0.0
                continue
            high = max(shift_means)
            low = min(shift_means)
            correlation[machine_id] = max(0.0, min(1.0, (high - low) / max(high, 1.0)))
        return correlation

    def machine_health_scores(self, rows: list[dict], shift_rows: list[dict], as_of_date: date) -> list[MachineSnapshot]:
        grouped = self._group_by_machine(rows)
        shift_corr = self._shift_scrap_correlation(shift_rows)
        snapshots: list[MachineSnapshot] = []
        for machine_id, history in grouped.items():
            if not history:
                continue
            snapshots.append(
                self._build_snapshot(
                    machine_id=machine_id,
                    as_of_date=as_of_date,
                    history=history,
                    shift_scrap_correlation=shift_corr.get(machine_id, 0.0),
                )
            )
        snapshots.sort(key=lambda s: s.health_score, reverse=True)
        return snapshots

    @staticmethod
    def _sample_features(history: list[dict], idx: int) -> list[float]:
        window_start = max(0, idx - 13)
        hist_window = history[window_start : idx + 1]
        downtime = [float(r["downtime_minutes"]) for r in hist_window]
        scrap = [float(r["scrap_units"]) for r in hist_window]
        output = [float(r["output_units"]) for r in hist_window]

        d_var = PredictiveIntelligenceEngine._normalized_variance(downtime)
        s_var = PredictiveIntelligenceEngine._normalized_variance(scrap)
        out_mean = abs(float(np.mean(output))) if output else 1.0
        out_slope = PredictiveIntelligenceEngine._slope(output)
        out_deg = min(1.0, max(0.0, -PredictiveIntelligenceEngine._safe_ratio(out_slope, out_mean)))

        d_mu = float(np.mean(downtime)) if downtime else 0.0
        d_sigma = float(np.std(downtime)) if downtime else 0.0
        s_mu = float(np.mean(scrap)) if scrap else 0.0
        s_sigma = float(np.std(scrap)) if scrap else 0.0
        anomaly = 0
        for row in hist_window:
            dz = 0.0 if d_sigma == 0 else abs((float(row["downtime_minutes"]) - d_mu) / d_sigma)
            sz = 0.0 if s_sigma == 0 else abs((float(row["scrap_units"]) - s_mu) / s_sigma)
            if dz >= 2.0 or sz >= 2.0:
                anomaly += 1
        anomaly_ratio = PredictiveIntelligenceEngine._safe_ratio(anomaly, max(len(hist_window), 1))

        return [d_var, anomaly_ratio, out_deg, s_var]

    @staticmethod
    def _failure_label(history: list[dict], idx: int, machine_downtime_p85: float, machine_scrap_p85: float) -> int:
        current_output_window = [float(r["output_units"]) for r in history[max(0, idx - 6) : idx + 1]]
        output_baseline = float(np.mean(current_output_window)) if current_output_window else 0.0
        future = history[idx + 1 : idx + 8]
        for row in future:
            downtime_flag = float(row["downtime_minutes"]) > machine_downtime_p85
            scrap_flag = float(row["scrap_percent"]) > machine_scrap_p85
            output_flag = output_baseline > 0 and float(row["output_units"]) < (0.7 * output_baseline)
            if downtime_flag or scrap_flag or output_flag:
                return 1
        return 0

    def build_training_data(self, rows: list[dict]) -> TrainingData:
        grouped = self._group_by_machine(rows)
        machine_ids: list[str] = []
        feature_rows: list[list[float]] = []
        labels: list[int] = []

        for machine_id, history in grouped.items():
            if len(history) < 15:
                continue
            machine_downtime_p85 = float(
                np.percentile([float(r["downtime_minutes"]) for r in history], 85)
            )
            machine_scrap_p85 = float(np.percentile([float(r["scrap_percent"]) for r in history], 85))

            for idx in range(7, len(history) - 7):
                feature_rows.append(self._sample_features(history, idx))
                labels.append(self._failure_label(history, idx, machine_downtime_p85, machine_scrap_p85))
                machine_ids.append(machine_id)

        if not feature_rows:
            return TrainingData(machine_ids=[], X=np.empty((0, 4), dtype=float), y=np.empty((0,), dtype=float))

        X = np.array(feature_rows, dtype=float)
        y = np.array(labels, dtype=float)
        return TrainingData(machine_ids=machine_ids, X=X, y=y)

    @staticmethod
    def _standardize(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
        return (X - mean) / std

    @staticmethod
    def _sigmoid_scalar(x: float) -> float:
        x = max(-40.0, min(40.0, x))
        return 1.0 / (1.0 + exp(-x))

    def _fit_feature_scaler(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        mean = np.mean(X, axis=0)
        std = np.std(X, axis=0)
        std = np.where(std == 0, 1.0, std)
        self.feature_mean = mean
        self.feature_std = std
        return mean, std

    def _make_synthetic_training(self, X_real: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if X_real.size == 0:
            X_syn = np.random.uniform(0.0, 1.0, (300, 4))
        else:
            real_mean = np.mean(X_real, axis=0)
            real_std = np.std(X_real, axis=0)
            real_std = np.where(real_std == 0, 0.1, real_std)
            sample_count = max(300, X_real.shape[0] * 2)
            X_syn = np.random.normal(loc=real_mean, scale=real_std, size=(sample_count, X_real.shape[1]))
            X_syn = np.clip(X_syn, 0.0, 1.5)

        logits = (
            1.9 * X_syn[:, 0]
            + 1.6 * X_syn[:, 1]
            + 1.3 * X_syn[:, 2]
            + 1.2 * X_syn[:, 3]
            - 2.5
        )
        probs = np.array([self._sigmoid_scalar(float(v)) for v in logits], dtype=float)
        y_syn = (probs > 0.5).astype(float)
        return X_syn, y_syn

    def train(self, training: TrainingData, as_of_date: date) -> tuple[float, float]:
        X_real = training.X
        y_real = training.y

        X_syn, y_syn = self._make_synthetic_training(X_real)

        scaler_source = X_real if X_real.size else X_syn
        mean, std = self._fit_feature_scaler(scaler_source)

        X_syn_scaled = self._standardize(X_syn, mean, std)
        self.model.fit(X_syn_scaled, y_syn, reset=True)

        accuracy = 0.0
        brier = 0.25
        if X_real.size and y_real.size:
            X_real_scaled = self._standardize(X_real, mean, std)
            split = max(1, int(0.8 * X_real_scaled.shape[0]))
            X_train, X_valid = X_real_scaled[:split], X_real_scaled[split:]
            y_train, y_valid = y_real[:split], y_real[split:]

            if X_train.size and y_train.size:
                self.model.fit(X_train, y_train, reset=False)

            if X_valid.size and y_valid.size:
                preds = self.model.predict_proba(X_valid)
                pred_labels = (preds >= 0.5).astype(float)
                accuracy = float(np.mean(pred_labels == y_valid))
                brier = float(np.mean((preds - y_valid) ** 2))
            else:
                preds = self.model.predict_proba(X_train)
                pred_labels = (preds >= 0.5).astype(float)
                accuracy = float(np.mean(pred_labels == y_train)) if y_train.size else 0.0
                brier = float(np.mean((preds - y_train) ** 2)) if y_train.size else 0.25

        self.last_trained_on = as_of_date
        return round(accuracy, 4), round(brier, 4)

    def infer_machine_risk(self, snapshots: list[MachineSnapshot]) -> list[MachineRisk]:
        if not snapshots:
            return []
        if self.feature_mean is None or self.feature_std is None:
            return [
                MachineRisk(
                    machine_id=s.machine_id,
                    failure_probability_next_7_days=round(s.health_score / 100.0, 4),
                    confidence_score=50.0,
                )
                for s in snapshots
            ]

        X = np.array(
            [
                [
                    s.rolling_downtime_variance,
                    s.anomaly_frequency,
                    s.output_degradation_trend,
                    s.scrap_variance,
                ]
                for s in snapshots
            ],
            dtype=float,
        )
        X_scaled = self._standardize(X, self.feature_mean, self.feature_std)
        probs = self.model.predict_proba(X_scaled)

        risks: list[MachineRisk] = []
        for idx, snapshot in enumerate(snapshots):
            probability = float(probs[idx])
            certainty = abs(probability - 0.5) * 2.0
            support = min(1.0, snapshot.data_points / 30.0)
            confidence = (0.6 * certainty + 0.4 * support) * 100.0
            risks.append(
                MachineRisk(
                    machine_id=snapshot.machine_id,
                    failure_probability_next_7_days=round(probability, 4),
                    confidence_score=round(confidence, 2),
                )
            )
        return risks

    @staticmethod
    def detect_drift(rows: list[dict]) -> list[DriftSignal]:
        grouped = PredictiveIntelligenceEngine._group_by_machine(rows)
        signals: list[DriftSignal] = []

        for machine_id, history in grouped.items():
            if len(history) < 20:
                continue

            recent = history[-14:]
            baseline = history[:-14]
            baseline = baseline[-30:] if len(baseline) > 30 else baseline
            if len(baseline) < 7:
                continue

            def metric(arr: list[dict], key: str) -> np.ndarray:
                return np.array([float(r[key]) for r in arr], dtype=float)

            concept_score = 0.0
            baseline_deviation_detected = False
            for key in ("downtime_minutes", "scrap_percent", "output_units"):
                recent_values = metric(recent, key)
                baseline_values = metric(baseline, key)
                b_mean = float(np.mean(baseline_values))
                r_mean = float(np.mean(recent_values))
                b_std = float(np.std(baseline_values)) or 1.0
                mean_shift = abs(r_mean - b_mean) / b_std
                concept_score += mean_shift
                if mean_shift >= 2.0:
                    baseline_deviation_detected = True

            concept_drift_detected = concept_score >= 3.0

            downtime_values = [float(r["downtime_minutes"]) for r in history[-30:]]
            best_score = 0.0
            best_idx: int | None = None
            for split in range(5, len(downtime_values) - 5):
                left = np.array(downtime_values[:split], dtype=float)
                right = np.array(downtime_values[split:], dtype=float)
                pooled_std = float(np.std(downtime_values)) or 1.0
                score = abs(float(np.mean(right)) - float(np.mean(left))) / pooled_std
                if score > best_score:
                    best_score = score
                    best_idx = split

            change_point_detected = best_score >= 1.5 and best_idx is not None
            change_point_date = None
            if change_point_detected and best_idx is not None:
                history_30 = history[-30:]
                change_point_date = history_30[best_idx]["date"]

            signals.append(
                DriftSignal(
                    machine_id=machine_id,
                    concept_drift_score=round(concept_score, 4),
                    concept_drift_detected=concept_drift_detected,
                    baseline_deviation_detected=baseline_deviation_detected,
                    change_point_detected=change_point_detected,
                    change_point_date=change_point_date,
                )
            )

        return signals

    @staticmethod
    def recommend(snapshot: MachineSnapshot) -> list[str]:
        recommendations: list[str] = []
        high_downtime_variance = snapshot.rolling_downtime_variance >= 0.35
        downtime_increasing = snapshot.downtime_trend > 0.0
        if high_downtime_variance and downtime_increasing:
            recommendations.append("Schedule maintenance inspection for stability issues")

        scrap_increasing = snapshot.scrap_trend > 0.0
        shift_correlated = snapshot.shift_scrap_correlation >= 0.15
        if scrap_increasing and shift_correlated:
            recommendations.append("Trigger operator retraining on shift-specific scrap handling")

        if not recommendations and snapshot.health_score >= 65:
            recommendations.append("Increase preventive checks and monitor output degradation")

        return recommendations

    def monitoring_snapshot(
        self,
        drift_signals: list[DriftSignal],
        accuracy: float,
        brier: float,
        as_of_date: date,
    ) -> MonitoringSnapshot:
        drifted = sum(1 for d in drift_signals if d.concept_drift_detected or d.change_point_detected)
        last_trained = self.last_trained_on or as_of_date
        retrain_days = 7
        if drifted > 0 or accuracy < 0.65:
            retrain_days = 1
        retrain_recommended_on = last_trained + timedelta(days=retrain_days)

        return MonitoringSnapshot(
            model_accuracy=round(accuracy, 4),
            brier_score=round(brier, 4),
            tracked_drift_machines=drifted,
            retrain_recommended_on=retrain_recommended_on,
            last_trained_on=last_trained,
        )
