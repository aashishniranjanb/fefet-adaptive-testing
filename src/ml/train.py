from sklearn.ensemble import RandomForestClassifier

def prepare_data(dataset):
    X, y = [], []
    for sample in dataset:
        X.append([
            sample.get("memory_window", 1.20 - sample.get("delta_vth", 0.0)),
            sample["Ncycles"],
            sample["T"],
            sample["Nwrites"]
        ])
        y.append(sample["best_test"])
    return X, y

def train_model(dataset):
    X, y = prepare_data(dataset)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    print("Model trained successfully.")
    return model
