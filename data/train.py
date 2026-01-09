"""
ML Training Pipeline
Train sklearn classifier từ collected data
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    accuracy_score,
    roc_auc_score
)
import joblib
import argparse
import os
import glob
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns


class ModelTrainer:
    """
    Train and evaluate fall detection classifier
    """
    
    def __init__(self, output_model_path: str = '../ai/models/fall_classifier.pkl'):
        self.output_model_path = output_model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        # Create models directory
        os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    
    def load_data(self, data_dir: str = 'datasets'):
        """
        Load all CSV files from data directory
        """
        # Find all CSV files
        csv_files = glob.glob(os.path.join(data_dir, 'features_*.csv'))
        
        if len(csv_files) == 0:
            raise ValueError(f"No CSV files found in {data_dir}")
        
        print(f"[TRAINER] Found {len(csv_files)} CSV files")
        
        # Load and concatenate
        dfs = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)
            print(f"  - {csv_file}: {len(df)} samples")
        
        # Concatenate
        data = pd.concat(dfs, ignore_index=True)
        
        print(f"\n[TRAINER] Total samples: {len(data)}")
        print(f"Label distribution:")
        print(data['label'].value_counts())
        
        return data
    
    def prepare_data(self, data: pd.DataFrame):
        """
        Prepare features and labels
        """
        # Separate features and labels
        X = data.drop('label', axis=1)
        y = data['label']
        
        # Convert labels to binary
        y = y.map({'fall': 1, 'not_fall': 0})
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Handle missing values
        X = X.fillna(0)
        
        # Check for infinite values
        X = X.replace([np.inf, -np.inf], 0)
        
        print(f"\n[TRAINER] Features: {X.shape[1]}")
        print(f"Samples: {X.shape[0]}")
        print(f"Fall samples: {y.sum()}")
        print(f"Not-fall samples: {(y == 0).sum()}")
        
        return X, y
    
    def train_model(
        self, 
        X_train, y_train, 
        model_type: str = 'random_forest'
    ):
        """
        Train classifier
        """
        print(f"\n[TRAINER] Training {model_type}...")
        
        # Standardize features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Select model
        if model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=42
            )
        elif model_type == 'svm':
            self.model = SVC(
                kernel='rbf',
                probability=True,
                class_weight='balanced',
                random_state=42
            )
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                class_weight='balanced',
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, 
            cv=5, scoring='accuracy'
        )
        
        print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    def evaluate_model(self, X_test, y_test, output_dir: str = 'training_results'):
        """
        Evaluate model on test set
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Scale test data
        X_test_scaled = self.scaler.transform(X_test)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n[EVALUATION]")
        print(f"Accuracy: {accuracy:.3f}")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=['not_fall', 'fall']
        ))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\nConfusion Matrix:")
        print(cm)
        
        # Save confusion matrix plot
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['not_fall', 'fall'],
            yticklabels=['not_fall', 'fall']
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
        print(f"\n[TRAINER] Confusion matrix saved to {output_dir}/confusion_matrix.png")
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1][:20]  # Top 20
            
            plt.figure(figsize=(10, 8))
            plt.barh(
                range(len(indices)),
                importances[indices]
            )
            plt.yticks(
                range(len(indices)),
                [self.feature_names[i] for i in indices]
            )
            plt.xlabel('Feature Importance')
            plt.title('Top 20 Important Features')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'feature_importance.png'))
            print(f"[TRAINER] Feature importance saved to {output_dir}/feature_importance.png")
        
        return accuracy
    
    def save_model(self):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, self.output_model_path)
        print(f"\n[TRAINER] Model saved to {self.output_model_path}")


def main():
    parser = argparse.ArgumentParser(description='Train Fall Detection Classifier')
    parser.add_argument(
        '--input',
        type=str,
        default='datasets',
        help='Input directory with CSV files (default: datasets)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='../ai/models/fall_classifier.pkl',
        help='Output model path (default: ../ai/models/fall_classifier.pkl)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='random_forest',
        choices=['logistic', 'svm', 'random_forest'],
        help='Model type (default: random_forest)'
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Test set size (default: 0.2)'
    )
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = ModelTrainer(output_model_path=args.output)
    
    try:
        # Load data
        data = trainer.load_data(args.input)
        
        # Prepare data
        X, y = trainer.prepare_data(data)
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=args.test_size,
            random_state=42,
            stratify=y
        )
        
        # Train
        trainer.train_model(X_train, y_train, model_type=args.model)
        
        # Evaluate
        accuracy = trainer.evaluate_model(X_test, y_test)
        
        # Save
        trainer.save_model()
        
        print("\n" + "="*50)
        print("Training completed successfully!")
        print(f"Final accuracy: {accuracy:.3f}")
        print(f"Model saved to: {args.output}")
        print("="*50)
        
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
