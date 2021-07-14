"""
Detects anomalous report data.
Evaluated on *every update* so therefore must be fast or threaded.
Should only include context irrelevant anomalies. That is, anomalies that don't depend on past/adjacent measurements.
Stores anomaly details in separate DB table.
"""
