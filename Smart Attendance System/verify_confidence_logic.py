
def calculate_confidence(score, threshold=0.25):
    if score > threshold:
        normalized = (score - threshold) / (1.0 - threshold)
        final_conf = 85 + (normalized * 15)
        return min(100, final_conf)
    return 0

print("Testing Confidence Calculation Logic:")
print(f"Threshold: 0.25")

scores_to_test = [0.20, 0.251, 0.26, 0.35, 0.50, 0.80, 0.95]

for score in scores_to_test:
    conf = calculate_confidence(score)
    print(f"Raw Score: {score:.3f} -> Calculated Confidence: {conf:.2f}%")
