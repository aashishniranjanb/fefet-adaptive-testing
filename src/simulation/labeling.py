from .fault_model import detect_fault, TESTS

def get_best_test(sample):
    results = {}
    for test in TESTS:
        detections = [detect_fault(sample, test) for _ in range(5)]
        results[test] = sum(detections)
        
    # choose test with highest detection success
    best_test = max(results, key=results.get)
    return best_test
