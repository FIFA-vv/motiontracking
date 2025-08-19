import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from sklearn import datasets

iris = datasets.load_iris()
X = iris.data   # Features
y = iris.target # Label

# Take only first two features (sepal length & width) for 2D plotting
X_vis = X[:, :2]
y_vis = y

# Split into train/test again for visualization
X_train_vis, X_test_vis, y_train_vis, y_test_vis = train_test_split(
    X_vis, y_vis, test_size=0.3, random_state=42
)

# Train model on 2 features for plotting
knn_vis = KNeighborsClassifier(n_neighbors=3)
knn_vis.fit(X_train_vis, y_train_vis)
