import numpy as np
import scipy.stats
from scipy.optimize import curve_fit


def smoothed_mean(data):
    (m, s), cov = smoothed_gauss_fit(data)
    return m


def smoothed_std(data):
    (m, s), cov = smoothed_gauss_fit(data)
    return s


def smoothed_std_std(data):
    (m, s), cov = smoothed_gauss_fit(data)
    return cov[1, 1] ** 0.5


def smoothed_gauss_fit_naive(data):
    def fit(data):
        return np.mean(data), np.std(data)

    for _ in range(3):
        m, s = fit(data)
        data = data[np.abs(data - np.median(data)) < 3 * s]

    return (m, s), np.zeros((2, 2))


def smoothed_gauss_fit(data):
    def fit(data):
        def gauss(x, m, s):
            return 1 / (s * (2 * np.pi) ** 0.5) * np.exp(-0.5 * ((x - m) / s) ** 2)

        if len(data) < 10:
            raise ValueError("Not enough data to fit a Gaussian")

        mean, std = np.mean(data), np.std(data)
        hist_range = (mean - 10 * std, mean + 10 * std)
        bins = max(10, int(len(data) ** 0.5))
        binned, edges = np.histogram(data, range=hist_range, bins=bins, density=True)
        centers = 0.5 * (edges[1:] + edges[:-1])
        params, cov = curve_fit(gauss, centers, binned)
        return params, cov

    def solve(data):
        for _ in range(3):
            (m, s), cov = fit(data)
            data = data[np.abs(data - m) < 3 * s]
        return (m, s), cov

    if len(data) == 0:
        return (0, 0), np.zeros((2, 2))

    try:
        return solve(data)
    except Exception as e:
        print(f"Falling back to naive mean/std. Error: {e}")
        return smoothed_gauss_fit_naive(data)


def clopper_pearson(k, n, alpha=0.32):
    """
    http://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval
    alpha confidence intervals for a binomial distribution of k expected successes on n trials
    Clopper Pearson intervals are a conservative estimate.
    """
    p = k / n
    if p == 1.0:
        return p, p, p
    p_upper = np.maximum(
        scipy.stats.beta.ppf(1 - alpha / 2, k + 1, n - k), np.zeros_like(p)
    )
    p_lower = np.minimum(scipy.stats.beta.ppf(alpha / 2, k, n - k + 1), np.ones_like(p))
    return p, p_upper, p_lower


def create_clopper_pearson_upper_bounds(alpha=0.32):
    def interval(data):
        _, p_upper, _ = clopper_pearson(np.sum(data), len(data), alpha)
        return p_upper

    return interval


def create_clopper_pearson_lower_bounds(alpha=0.32):
    def interval(data):
        _, _, p_lower = clopper_pearson(np.sum(data), len(data), alpha)
        return p_lower

    return interval
