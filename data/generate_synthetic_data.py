"""
Generate Synthetic Training Data
For demo and testing purposes
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_fall_features(n_samples=200):
    """Generate synthetic features for fall scenarios"""
    features = []
    
    for i in range(n_samples):
        # Simulate fall characteristics
        feature = {
            # High aspect ratio (lying down)
            'aspect_ratio_mean': np.random.uniform(1.8, 3.0),
            'aspect_ratio_std': np.random.uniform(0.1, 0.3),
            'aspect_ratio_min': np.random.uniform(1.5, 2.5),
            'aspect_ratio_max': np.random.uniform(2.5, 3.5),
            'aspect_ratio_range': np.random.uniform(0.5, 1.5),
            
            # Horizontal angle
            'angle_mean': np.random.uniform(70, 110),
            'angle_std': np.random.uniform(5, 15),
            'angle_min': np.random.uniform(60, 80),
            'angle_max': np.random.uniform(100, 120),
            'angle_range': np.random.uniform(20, 40),
            
            # Low centroid (bottom of frame)
            'centroid_y_mean': np.random.uniform(0.7, 0.95),
            'centroid_y_std': np.random.uniform(0.02, 0.08),
            'centroid_y_min': np.random.uniform(0.6, 0.8),
            'centroid_y_max': np.random.uniform(0.85, 0.99),
            'centroid_y_range': np.random.uniform(0.1, 0.3),
            
            # Small height (lying)
            'bbox_height_mean': np.random.uniform(40, 80),
            'bbox_height_std': np.random.uniform(5, 15),
            'bbox_height_min': np.random.uniform(30, 60),
            'bbox_height_max': np.random.uniform(60, 100),
            'bbox_height_range': np.random.uniform(10, 40),
            
            # Fast downward velocity
            'velocity_y_mean': np.random.uniform(8, 20),
            'velocity_y_std': np.random.uniform(2, 6),
            'velocity_y_min': np.random.uniform(5, 12),
            'velocity_y_max': np.random.uniform(15, 30),
            'velocity_y_range': np.random.uniform(8, 20),
            
            # High velocity magnitude
            'velocity_magnitude_mean': np.random.uniform(10, 25),
            'velocity_magnitude_std': np.random.uniform(3, 8),
            'velocity_magnitude_min': np.random.uniform(5, 15),
            'velocity_magnitude_max': np.random.uniform(18, 35),
            'velocity_magnitude_range': np.random.uniform(10, 25),
            
            # Temporal features
            'aspect_ratio_trend': np.random.uniform(0.5, 2.0),
            'centroid_y_change': np.random.uniform(0.2, 0.5),
            'centroid_y_speed': np.random.uniform(0.01, 0.03),
            'height_change': np.random.uniform(-80, -20),
            'height_change_ratio': np.random.uniform(-0.6, -0.2),
            'peak_velocity_y': np.random.uniform(15, 35),
            'current_aspect_ratio': np.random.uniform(2.0, 3.5),
            'current_centroid_y': np.random.uniform(0.8, 0.95),
            'current_angle': np.random.uniform(75, 105),
            
            'label': 'fall'
        }
        features.append(feature)
    
    return features


def generate_not_fall_features(n_samples=400):
    """Generate synthetic features for not-fall scenarios"""
    features = []
    
    for i in range(n_samples):
        # Simulate normal activities (standing, walking, sitting)
        activity = np.random.choice(['standing', 'walking', 'sitting'])
        
        if activity == 'standing':
            feature = {
                # Low aspect ratio (vertical)
                'aspect_ratio_mean': np.random.uniform(0.3, 0.6),
                'aspect_ratio_std': np.random.uniform(0.02, 0.1),
                'aspect_ratio_min': np.random.uniform(0.25, 0.5),
                'aspect_ratio_max': np.random.uniform(0.4, 0.7),
                'aspect_ratio_range': np.random.uniform(0.1, 0.3),
                
                # Vertical angle
                'angle_mean': np.random.uniform(0, 30),
                'angle_std': np.random.uniform(2, 10),
                'angle_min': np.random.uniform(0, 15),
                'angle_max': np.random.uniform(20, 40),
                'angle_range': np.random.uniform(5, 25),
                
                # High centroid (top of frame)
                'centroid_y_mean': np.random.uniform(0.2, 0.5),
                'centroid_y_std': np.random.uniform(0.02, 0.08),
                'centroid_y_min': np.random.uniform(0.15, 0.4),
                'centroid_y_max': np.random.uniform(0.35, 0.6),
                'centroid_y_range': np.random.uniform(0.1, 0.25),
                
                # Large height (standing)
                'bbox_height_mean': np.random.uniform(150, 220),
                'bbox_height_std': np.random.uniform(5, 20),
                'bbox_height_min': np.random.uniform(130, 180),
                'bbox_height_max': np.random.uniform(170, 240),
                'bbox_height_range': np.random.uniform(20, 60),
                
                # Slow velocity
                'velocity_y_mean': np.random.uniform(0, 3),
                'velocity_y_std': np.random.uniform(0.5, 2),
                'velocity_y_min': np.random.uniform(0, 1),
                'velocity_y_max': np.random.uniform(2, 5),
                'velocity_y_range': np.random.uniform(1, 4),
                
                'velocity_magnitude_mean': np.random.uniform(0, 4),
                'velocity_magnitude_std': np.random.uniform(0.5, 2),
                'velocity_magnitude_min': np.random.uniform(0, 2),
                'velocity_magnitude_max': np.random.uniform(3, 6),
                'velocity_magnitude_range': np.random.uniform(2, 5),
            }
        
        elif activity == 'walking':
            feature = {
                'aspect_ratio_mean': np.random.uniform(0.35, 0.65),
                'aspect_ratio_std': np.random.uniform(0.05, 0.15),
                'aspect_ratio_min': np.random.uniform(0.3, 0.5),
                'aspect_ratio_max': np.random.uniform(0.5, 0.8),
                'aspect_ratio_range': np.random.uniform(0.15, 0.4),
                
                'angle_mean': np.random.uniform(5, 35),
                'angle_std': np.random.uniform(3, 12),
                'angle_min': np.random.uniform(0, 20),
                'angle_max': np.random.uniform(25, 50),
                'angle_range': np.random.uniform(10, 35),
                
                'centroid_y_mean': np.random.uniform(0.25, 0.55),
                'centroid_y_std': np.random.uniform(0.03, 0.1),
                'centroid_y_min': np.random.uniform(0.2, 0.45),
                'centroid_y_max': np.random.uniform(0.4, 0.65),
                'centroid_y_range': np.random.uniform(0.15, 0.3),
                
                'bbox_height_mean': np.random.uniform(140, 210),
                'bbox_height_std': np.random.uniform(8, 25),
                'bbox_height_min': np.random.uniform(120, 180),
                'bbox_height_max': np.random.uniform(170, 230),
                'bbox_height_range': np.random.uniform(30, 70),
                
                'velocity_y_mean': np.random.uniform(0, 5),
                'velocity_y_std': np.random.uniform(1, 3),
                'velocity_y_min': np.random.uniform(0, 2),
                'velocity_y_max': np.random.uniform(4, 8),
                'velocity_y_range': np.random.uniform(3, 7),
                
                'velocity_magnitude_mean': np.random.uniform(2, 8),
                'velocity_magnitude_std': np.random.uniform(1, 4),
                'velocity_magnitude_min': np.random.uniform(1, 4),
                'velocity_magnitude_max': np.random.uniform(6, 12),
                'velocity_magnitude_range': np.random.uniform(4, 10),
            }
        
        else:  # sitting
            feature = {
                'aspect_ratio_mean': np.random.uniform(0.8, 1.4),
                'aspect_ratio_std': np.random.uniform(0.05, 0.15),
                'aspect_ratio_min': np.random.uniform(0.7, 1.2),
                'aspect_ratio_max': np.random.uniform(1.0, 1.6),
                'aspect_ratio_range': np.random.uniform(0.2, 0.5),
                
                'angle_mean': np.random.uniform(30, 60),
                'angle_std': np.random.uniform(3, 12),
                'angle_min': np.random.uniform(20, 50),
                'angle_max': np.random.uniform(40, 70),
                'angle_range': np.random.uniform(10, 30),
                
                'centroid_y_mean': np.random.uniform(0.5, 0.75),
                'centroid_y_std': np.random.uniform(0.03, 0.1),
                'centroid_y_min': np.random.uniform(0.45, 0.65),
                'centroid_y_max': np.random.uniform(0.6, 0.85),
                'centroid_y_range': np.random.uniform(0.1, 0.25),
                
                'bbox_height_mean': np.random.uniform(90, 140),
                'bbox_height_std': np.random.uniform(5, 20),
                'bbox_height_min': np.random.uniform(70, 120),
                'bbox_height_max': np.random.uniform(110, 160),
                'bbox_height_range': np.random.uniform(20, 50),
                
                'velocity_y_mean': np.random.uniform(0, 2),
                'velocity_y_std': np.random.uniform(0.3, 1.5),
                'velocity_y_min': np.random.uniform(0, 0.5),
                'velocity_y_max': np.random.uniform(1, 4),
                'velocity_y_range': np.random.uniform(0.5, 3),
                
                'velocity_magnitude_mean': np.random.uniform(0, 3),
                'velocity_magnitude_std': np.random.uniform(0.3, 2),
                'velocity_magnitude_min': np.random.uniform(0, 1),
                'velocity_magnitude_max': np.random.uniform(2, 5),
                'velocity_magnitude_range': np.random.uniform(1, 4),
            }
        
        # Common temporal features
        feature.update({
            'aspect_ratio_trend': np.random.uniform(-0.2, 0.2),
            'centroid_y_change': np.random.uniform(-0.1, 0.1),
            'centroid_y_speed': np.random.uniform(-0.005, 0.005),
            'height_change': np.random.uniform(-20, 20),
            'height_change_ratio': np.random.uniform(-0.15, 0.15),
            'peak_velocity_y': np.random.uniform(2, 10),
            'current_aspect_ratio': np.random.uniform(0.3, 1.5),
            'current_centroid_y': np.random.uniform(0.2, 0.7),
            'current_angle': np.random.uniform(0, 60),
            'label': 'not_fall'
        })
        
        features.append(feature)
    
    return features


def main():
    print("="*70)
    print("SYNTHETIC DATA GENERATION FOR TRAINING")
    print("="*70 + "\n")
    
    # Create datasets directory
    os.makedirs('datasets', exist_ok=True)
    
    # Generate fall data
    print("[1/3] Generating fall scenarios...")
    fall_data = generate_fall_features(n_samples=200)
    print(f"      ✓ Generated {len(fall_data)} fall samples")
    
    # Generate not-fall data
    print("[2/3] Generating not-fall scenarios...")
    not_fall_data = generate_not_fall_features(n_samples=400)
    print(f"      ✓ Generated {len(not_fall_data)} not-fall samples")
    
    # Combine and save
    print("[3/3] Saving to CSV...")
    all_data = fall_data + not_fall_data
    df = pd.DataFrame(all_data)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'datasets/features_synthetic_{timestamp}.csv'
    df.to_csv(filename, index=False)
    
    print(f"      ✓ Saved to {filename}")
    print(f"\n{'='*70}")
    print("DATA SUMMARY")
    print(f"{'='*70}")
    print(f"Total samples: {len(df)}")
    print(f"Fall samples: {len(df[df['label'] == 'fall'])}")
    print(f"Not-fall samples: {len(df[df['label'] == 'not_fall'])}")
    print(f"Features: {len(df.columns) - 1}")
    print(f"\n✓ Ready for training!")
    print(f"\nNext step:")
    print(f"  python train.py")
    print(f"  # or")
    print(f"  python train_advanced.py")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
