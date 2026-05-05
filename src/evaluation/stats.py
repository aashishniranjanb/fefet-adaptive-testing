import numpy as np

def mean_ci_95_binary(x):
    """
    x: list/array of 0/1 detections
    returns (mean, lower, upper) in percentage
    """
    x = np.asarray(x)
    n = len(x)
    if n == 0:
        return 0.0, 0.0, 0.0

    p = np.mean(x)
    # normal approximation (OK for n>=30)
    se = np.sqrt(p * (1 - p) / n)
    z = 1.96

    lo = max(0.0, p - z * se)
    hi = min(1.0, p + z * se)

    return 100*p, 100*lo, 100*hi
