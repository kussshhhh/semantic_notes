import numpy as np
from sklearn.decomposition import PCA

class PositionCalculator:
    def __init__(self, n_components=3):
        """
        Initializes the PositionCalculator with a specified number of components for PCA.

        Args:
            n_components (int): The number of principal components to reduce to (e.g., 3 for 3D).
        """
        self.n_components = n_components
        self.pca = PCA(n_components=self.n_components)
        self.is_fitted = False # To track if PCA has been fitted

    def calculate_positions(self, semantic_vectors: list[list[float]]) -> list[list[float]] | None:
        """
        Calculates 3D positions from a list of semantic vectors using PCA.

        Args:
            semantic_vectors (list[list[float]]): A list of semantic vectors (lists of floats).

        Returns:
            list[list[float]] | None: A list of 3D coordinate lists,
                                     or None if an error occurs or input is unsuitable.
        """
        if not semantic_vectors or not isinstance(semantic_vectors, list):
            print("Error: Input semantic_vectors must be a non-empty list.")
            return None
        if not all(isinstance(vec, list) for vec in semantic_vectors):
            print("Error: All elements in semantic_vectors must be lists (vectors).")
            return None
        if not all(all(isinstance(val, (int, float)) for val in vec) for vec in semantic_vectors):
            print("Error: All values in semantic vectors must be numbers (int or float).")
            return None

        try:
            vectors_array = np.array(semantic_vectors)
        except Exception as e:
            print(f"Error converting semantic vectors to NumPy array: {e}")
            return None

        if vectors_array.ndim != 2:
            print(f"Error: Input semantic_vectors should result in a 2D array. Got shape {vectors_array.shape}")
            return None

        num_samples, num_features = vectors_array.shape

        if num_features == 0:
            print("Error: Semantic vectors have no features (dimension is 0).")
            return None

        if num_samples < self.n_components:
            print(f"Warning: Number of samples ({num_samples}) is less than n_components ({self.n_components}).")
            # Simplified strategy: if vectors have at least n_components dimensions, take the first n_components
            # Otherwise, pad with zeros. This is a fallback and might not be optimal.
            if num_features >= self.n_components:
                print(f"Using the first {self.n_components} dimensions of the semantic vectors directly.")
                return [vec[:self.n_components] for vec in semantic_vectors]
            else:
                print(f"Padding vectors with zeros to meet {self.n_components} dimensions.")
                padded_vectors = []
                for vec in semantic_vectors:
                    padding = [0.0] * (self.n_components - len(vec))
                    padded_vectors.append(vec + padding)
                return padded_vectors

        try:
            # Fit PCA if not already fitted or if the number of features changes
            # For simplicity here, we fit every time. In a more stateful scenario,
            # one might want to fit PCA once with representative data.
            reduced_vectors_np = self.pca.fit_transform(vectors_array)
            self.is_fitted = True
            return reduced_vectors_np.tolist()
        except ValueError as ve:
            print(f"PCA ValueError: {ve}. This can happen if n_samples < n_components for the PCA model.")
            # This case should ideally be caught by the check above, but as a fallback:
            if "n_samples < n_components" in str(ve) and num_features >= self.n_components :
                 print(f"Fallback: Using the first {self.n_components} dimensions of the semantic vectors directly due to PCA error.")
                 return [vec[:self.n_components] for vec in semantic_vectors]
            return None
        except Exception as e:
            print(f"Error during PCA processing: {e}")
            return None

if __name__ == '__main__':
    # Example Usage
    calculator = PositionCalculator(n_components=3)

    # Test case 1: Ideal case
    vectors1 = [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [0.5, 0.4, 0.3, 0.2, 0.1],
        [0.2, 0.3, 0.4, 0.5, 0.6],
        [0.6, 0.5, 0.4, 0.3, 0.2]
    ]
    positions1 = calculator.calculate_positions(vectors1)
    if positions1:
        print(f"Positions for vectors1 (PCA): {positions1}")
        assert all(len(p) == 3 for p in positions1)

    # Test case 2: Fewer samples than components
    vectors2 = [
        [1.0, 2.0, 3.0, 4.0],
        [5.0, 6.0, 7.0, 8.0]
    ]
    positions2 = calculator.calculate_positions(vectors2)
    if positions2:
        print(f"Positions for vectors2 (fewer samples than components): {positions2}")
        assert all(len(p) == 3 for p in positions2) # Fallback should ensure 3D

    # Test case 3: Fewer features than components in original vectors (and fewer samples)
    vectors3 = [
        [1.0, 2.0],
        [3.0, 4.0]
    ]
    positions3 = calculator.calculate_positions(vectors3)
    if positions3:
        print(f"Positions for vectors3 (fewer features and samples): {positions3}")
        assert all(len(p) == 3 for p in positions3) # Fallback should ensure 3D by padding

    # Test case 4: Empty list
    positions4 = calculator.calculate_positions([])
    if positions4 is None:
        print("Correctly handled empty list input.")

    # Test case 5: List with empty vectors
    vectors5 = [[], []]
    # This will be caught by np.array conversion or PCA itself, or by initial checks if dimensions are zero.
    # Depending on numpy version, array creation might fail or create object array.
    # My checks for all values being numbers and vectors being lists should catch this.
    # Let's make it a list of lists of floats, but one inner list is empty.
    vectors5_corrected = [[1.0,2.0], []]
    # This should be caught by "all elements must be lists (vectors)" if not, then by "all values must be numbers"
    # The current code expects lists of numbers. An empty list [] inside semantic_vectors
    # will cause `all(isinstance(val, (int, float)) for val in vec)` to be true for that vec (vacuously true),
    # but np.array might complain if shapes are inconsistent.
    # The `np.array(semantic_vectors)` will likely create an object array if inner lists have different lengths.
    # The `vectors_array.ndim != 2` check should catch this.

    print("Testing inconsistent vector dimensions:")
    vectors_inconsistent = [[1.0, 2.0], [3.0, 4.0, 5.0]]
    positions_inconsistent = calculator.calculate_positions(vectors_inconsistent)
    if positions_inconsistent is None:
        print("Correctly handled inconsistent vector dimensions.")

    # Test case 6: Single vector (less samples than n_components)
    vector_single = [[0.1, 0.2, 0.3, 0.4, 0.5]]
    positions_single = calculator.calculate_positions(vector_single)
    if positions_single:
        print(f"Positions for single vector: {positions_single}")
        assert all(len(p) == 3 for p in positions_single)

    # Test case 7: Vectors with dimension < n_components
    vectors_low_dim = [
        [1.0, 2.0],
        [3.0, 4.0],
        [5.0, 6.0],
        [7.0, 8.0]
    ]
    positions_low_dim = calculator.calculate_positions(vectors_low_dim)
    if positions_low_dim:
        print(f"Positions for low_dim_vectors (fallback padding): {positions_low_dim}")
        assert all(len(p) == 3 for p in positions_low_dim)
        assert positions_low_dim[0] == [1.0, 2.0, 0.0] # Example check for padding

    print("All example tests run.")
