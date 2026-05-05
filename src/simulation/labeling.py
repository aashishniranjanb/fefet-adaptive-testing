from .fault_model import detect_fault, TESTS

def get_best_test(sample):
    # deterministic preference with small Monte Carlo smoothing
    scores = {}
    
    for test in TESTS:
        trials = [detect_fault(sample, test) for _ in range(7)]
        scores[test] = sum(trials)
        
    return max(scores, key=scores.get)
