"""
Advanced Training Script with XGBoost and Ensemble
Supports multiple models and hyperparameter tuning
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    accuracy_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve
)
import joblib
import argparse
import os
import glob
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


class AdvancedTrainer:
    """Advanced ML training with XGBoost and optimization"""
    
    def __init__(self, output_dir='../ai/models'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_score = 0
    
    def load_data(self, data_dir='datasets'):
        """Load training data"""
        csv_files = glob.glob(os.path.join(data_dir, 'features_*.csv'))
        
        if not csv_files:
            raise ValueError(f"No CSV files found in {data_dir}")
        
        print(f"\n{'='*60}")
        print(f"ADVANCED TRAINING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        print(f"[DATA] Loading {len(csv_files)} CSV files...")
        
        dfs = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)
            print(f"  ✓ {os.path.basename(csv_file)}: {len(df)} samples")
        
        data = pd.concat(dfs, ignore_index=True)
        
        print(f"\n[DATA] Total: {len(data)} samples")
        print(f"[DATA] Fall: {(data['label'] == 'fall').sum()}")
        print(f"[DATA] Not Fall: {(data['label'] == 'not_fall').sum()}")
        
        return data
    
    def prepare_data(self, data):
        """Prepare and clean data"""
        print(f"\n[PREP] Preparing data...")
        
        # Separate features and labels
        X = data.drop('label', axis=1)
        y = data['label'].map({'fall': 1, 'not_fall': 0})
        
        # Handle missing/infinite values
        X = X.fillna(0)
        X = X.replace([np.inf, -np.inf], 0)
        
        # Feature names
        feature_names = X.columns.tolist()
        
        print(f"  ✓ Features: {len(feature_names)}")
        print(f"  ✓ Samples: {len(X)}")
        
        return X, y, feature_names
    
    def train_xgboost(self, X_train, y_train, X_test, y_test, optimize=False):
        """Train XGBoost model"""
        try:
            import xgboost as xgb
        except ImportError:
            print("[ERROR] XGBoost not installed: pip install xgboost")
            return None
        
        print(f"\n[XGBOOST] Training XGBoost...")
        
        if optimize:
            # Grid search
            param_grid = {
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3],
                'n_estimators': [100, 200],
                'min_child_weight': [1, 3, 5],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0]
            }
            
            print("  Running Grid Search...")
            xgb_model = xgb.XGBClassifier(
                objective='binary:logistic',
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            
            grid = GridSearchCV(
                xgb_model,
                param_grid,
                cv=5,
                scoring='roc_auc',
                n_jobs=-1,
                verbose=1
            )
            
            grid.fit(X_train, y_train)
            model = grid.best_estimator_
            
            print(f"  ✓ Best params: {grid.best_params_}")
            print(f"  ✓ Best CV score: {grid.best_score_:.4f}")
            
        else:
            # Default params
            model = xgb.XGBClassifier(
                max_depth=5,
                learning_rate=0.1,
                n_estimators=200,
                min_child_weight=3,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='binary:logistic',
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            
            model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=20,
                verbose=False
            )
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        print(f"  ✓ Test Accuracy: {accuracy:.4f}")
        print(f"  ✓ Test AUC: {auc:.4f}")
        
        return {
            'model': model,
            'accuracy': accuracy,
            'auc': auc,
            'predictions': {'y_test': y_test, 'y_pred': y_pred, 'y_proba': y_proba}
        }
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Train Random Forest"""
        from sklearn.ensemble import RandomForestClassifier
        
        print(f"\n[RF] Training Random Forest...")
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        print(f"  ✓ Test Accuracy: {accuracy:.4f}")
        print(f"  ✓ Test AUC: {auc:.4f}")
        
        return {
            'model': model,
            'accuracy': accuracy,
            'auc': auc,
            'predictions': {'y_test': y_test, 'y_pred': y_pred, 'y_proba': y_proba}
        }
    
    def train_all(self, X, y, feature_names, test_size=0.2, optimize_xgb=False):
        """Train all models and compare"""
        print(f"\n[TRAINING] Training all models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Train XGBoost
        xgb_result = self.train_xgboost(X_train, y_train, X_test, y_test, optimize_xgb)
        if xgb_result:
            self.models['xgboost'] = xgb_result
        
        # Train Random Forest
        rf_result = self.train_random_forest(X_train, y_train, X_test, y_test)
        self.models['random_forest'] = rf_result
        
        # Find best model
        for name, result in self.models.items():
            if result['auc'] > self.best_score:
                self.best_score = result['auc']
                self.best_model = name
        
        print(f"\n[RESULT] Best model: {self.best_model.upper()} (AUC: {self.best_score:.4f})")
        
        return self.models
    
    def save_models(self, feature_names):
        """Save all trained models"""
        print(f"\n[SAVE] Saving models...")
        
        for name, result in self.models.items():
            model_data = {
                'model': result['model'],
                'feature_names': feature_names,
                'accuracy': result['accuracy'],
                'auc': result['auc'],
                'trained_at': datetime.now().isoformat()
            }
            
            if name == 'xgboost':
                save_path = os.path.join(self.output_dir, 'xgboost_fall_classifier.pkl')
            else:
                save_path = os.path.join(self.output_dir, 'fall_classifier.pkl')
            
            joblib.dump(model_data, save_path)
            print(f"  ✓ {name}: {save_path}")
        
        # Save metadata
        metadata = {
            'best_model': self.best_model,
            'best_auc': self.best_score,
            'models': {
                name: {
                    'accuracy': result['accuracy'],
                    'auc': result['auc']
                }
                for name, result in self.models.items()
            },
            'trained_at': datetime.now().isoformat()
        }
        
        metadata_path = os.path.join(self.output_dir, 'training_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✓ Metadata: {metadata_path}")
    
    def plot_results(self):
        """Plot training results"""
        print(f"\n[PLOT] Generating plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Model comparison
        ax = axes[0, 0]
        models_names = list(self.models.keys())
        accuracies = [self.models[m]['accuracy'] for m in models_names]
        aucs = [self.models[m]['auc'] for m in models_names]
        
        x = np.arange(len(models_names))
        width = 0.35
        
        ax.bar(x - width/2, accuracies, width, label='Accuracy', alpha=0.8)
        ax.bar(x + width/2, aucs, width, label='AUC', alpha=0.8)
        ax.set_ylabel('Score')
        ax.set_title('Model Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels([m.replace('_', ' ').title() for m in models_names])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # 2. ROC Curves
        ax = axes[0, 1]
        for name, result in self.models.items():
            pred = result['predictions']
            fpr, tpr, _ = roc_curve(pred['y_test'], pred['y_proba'])
            ax.plot(fpr, tpr, label=f"{name} (AUC={result['auc']:.3f})", linewidth=2)
        
        ax.plot([0, 1], [0, 1], 'k--', label='Random', alpha=0.3)
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('ROC Curves')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # 3. Confusion Matrix (best model)
        ax = axes[1, 0]
        best_result = self.models[self.best_model]
        cm = confusion_matrix(
            best_result['predictions']['y_test'],
            best_result['predictions']['y_pred']
        )
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title(f'Confusion Matrix - {self.best_model.title()}')
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')
        
        # 4. Feature Importance (XGBoost)
        ax = axes[1, 1]
        if 'xgboost' in self.models:
            model = self.models['xgboost']['model']
            importance = model.feature_importances_
            indices = np.argsort(importance)[-10:]
            
            feature_names = model.get_booster().feature_names
            if feature_names:
                labels = [feature_names[i] for i in indices]
            else:
                labels = [f'Feature {i}' for i in indices]
            
            ax.barh(range(len(indices)), importance[indices])
            ax.set_yticks(range(len(indices)))
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_xlabel('Importance')
            ax.set_title('Top 10 Features (XGBoost)')
            ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        plot_path = os.path.join(self.output_dir, 'training_results.png')
        plt.savefig(plot_path, dpi=150)
        print(f"  ✓ Plot saved: {plot_path}")
        
        plt.close()
    
    def print_summary(self):
        """Print training summary"""
        print(f"\n{'='*60}")
        print("TRAINING SUMMARY")
        print(f"{'='*60}\n")
        
        for name, result in self.models.items():
            print(f"{name.upper()}")
            print(f"  Accuracy: {result['accuracy']:.4f}")
            print(f"  AUC:      {result['auc']:.4f}")
            
            pred = result['predictions']
            cm = confusion_matrix(pred['y_test'], pred['y_pred'])
            
            tn, fp, fn, tp = cm.ravel()
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall:    {recall:.4f}")
            print(f"  F1 Score:  {f1:.4f}")
            print()
        
        print(f"✓ Best Model: {self.best_model.upper()}")
        print(f"✓ Models saved to: {self.output_dir}")
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Advanced Fall Detection Training')
    parser.add_argument('--data-dir', default='datasets', help='Data directory')
    parser.add_argument('--output-dir', default='../ai/models', help='Output directory')
    parser.add_argument('--optimize', action='store_true', help='Run hyperparameter optimization')
    parser.add_argument('--test-size', type=float, default=0.2, help='Test split ratio')
    
    args = parser.parse_args()
    
    try:
        # Initialize trainer
        trainer = AdvancedTrainer(args.output_dir)
        
        # Load data
        data = trainer.load_data(args.data_dir)
        
        # Prepare data
        X, y, feature_names = trainer.prepare_data(data)
        
        # Train all models
        trainer.train_all(X, y, feature_names, args.test_size, args.optimize)
        
        # Save models
        trainer.save_models(feature_names)
        
        # Plot results
        trainer.plot_results()
        
        # Print summary
        trainer.print_summary()
        
        print("✓ Training complete!")
        print(f"\nTo use the best model, update config.yaml:")
        print(f"  ml_classifier:")
        print(f"    enabled: true")
        if trainer.best_model == 'xgboost':
            print(f"    use_xgboost: true")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
