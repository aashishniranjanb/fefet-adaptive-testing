from src.dataset.generate import generate_dataset
from src.simulation.labeling import get_best_test
from src.ml.train import train_model

def main():
    print("Generating dataset...")
    data = generate_dataset(n=3000)
    
    print("Labeling dataset with best tests...")
    for sample in data:
        sample["best_test"] = get_best_test(sample)
        
    print("Training ML model...")
    model = train_model(data)
    
    print("Pipeline executed successfully!")

if __name__ == "__main__":
    main()
