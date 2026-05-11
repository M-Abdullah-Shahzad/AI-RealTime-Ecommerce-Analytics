"""
MODULE 7 - AI-BASED CHURN PREDICTION
=====================================
Machine learning model to predict customer churn.

Churn Definition:
- No purchase in last 90 days = churned

Features:
- Recency, Frequency, Monetary
- Average Order Value
- Purchase Count
- Total Spending

Model: Random Forest Classifier
Framework: Scikit-learn + Spark MLlib

Metrics:
- Accuracy, Precision, Recall, F1-Score
- Confusion Matrix, ROC-AUC
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import warnings
warnings.filterwarnings('ignore')

import sys
import io
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Scikit-learn imports
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve, auc
)

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")


class ChurnPredictionModel:
    """ML model for customer churn prediction"""
    
    def __init__(self, cleaned_data_path, rfm_data_path=None):
        self.df = pd.read_csv(cleaned_data_path)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.rfm_df = pd.read_csv(rfm_data_path) if rfm_data_path else None
        
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.scaler = None
        self.feature_names = None
        
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"🤖 {title}")
        print("="*80)
    
    def define_churn_label(self, churn_days=90):
        """Define churn: no purchase in last N days"""
        print("\n" + "="*80)
        print("📊 DEFINING CHURN LABEL")
        print("="*80)
        
        reference_date = self.df['InvoiceDate'].max() + timedelta(days=1)
        print(f"\n📅 Reference Date: {reference_date.date()}")
        print(f"🎯 Churn Definition: No purchase in last {churn_days} days")
        
        # Calculate recency for each customer
        customer_recency = self.df.groupby('CustomerID')['InvoiceDate'].max().reset_index()
        customer_recency.columns = ['CustomerID', 'LastPurchaseDate']
        customer_recency['DaysSinceLastPurchase'] = (
            reference_date - customer_recency['LastPurchaseDate']
        ).dt.days
        customer_recency['IsChurned'] = (
            customer_recency['DaysSinceLastPurchase'] >= churn_days
        ).astype(int)
        
        churn_count = customer_recency['IsChurned'].sum()
        active_count = len(customer_recency) - churn_count
        
        print(f"\n📊 Churn Statistics:")
        print(f"   • Active Customers: {active_count:,} ({active_count/len(customer_recency)*100:.1f}%)")
        print(f"   • Churned Customers: {churn_count:,} ({churn_count/len(customer_recency)*100:.1f}%)")
        print(f"   • Total Customers: {len(customer_recency):,}")
        
        return customer_recency
    
    def create_features(self, churn_df, churn_days=90):
        """Create features for ML model"""
        self.print_header("FEATURE ENGINEERING")
        
        # Calculate RFM metrics
        reference_date = self.df['InvoiceDate'].max() + timedelta(days=1)
        
        customer_features = self.df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
            'InvoiceNo': 'count',  # Frequency
            'TotalPrice': ['sum', 'mean', 'std'],  # Monetary metrics
            'Quantity': 'sum'  # Total items
        }).reset_index()
        
        # Flatten column names
        customer_features.columns = [
            'CustomerID', 'Recency', 'Frequency', 'TotalMonetary',
            'AvgOrderValue', 'StdOrderValue', 'TotalQuantity'
        ]
        
        # Fill NaN std values
        customer_features['StdOrderValue'].fillna(0, inplace=True)
        
        # Additional features
        customer_features['AvgItemsPerOrder'] = (
            customer_features['TotalQuantity'] / customer_features['Frequency']
        )
        customer_features['RepeatPurchaseRate'] = (
            (customer_features['Frequency'] - 1) / 365 * 100
        ).clip(lower=0)
        
        # Merge with churn labels
        features_df = customer_features.merge(
            churn_df[['CustomerID', 'IsChurned']],
            on='CustomerID'
        )
        
        print(f"\n✓ Features created for {len(features_df):,} customers")
        print(f"\n📊 Features:")
        features_list = ['Recency', 'Frequency', 'TotalMonetary', 'AvgOrderValue',
                        'StdOrderValue', 'TotalQuantity', 'AvgItemsPerOrder', 'RepeatPurchaseRate']
        for i, feat in enumerate(features_list, 1):
            print(f"   {i}. {feat}")
        
        print(f"\n📈 Feature Statistics:")
        print(features_df[features_list].describe().round(2))
        
        self.feature_names = features_list
        return features_df
    
    def prepare_data(self, features_df, test_size=0.2, random_state=42):
        """Prepare training and testing data"""
        self.print_header("DATA PREPARATION")
        
        X = features_df[self.feature_names].values
        y = features_df['IsChurned'].values
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.X_train = X_train_scaled
        self.X_test = X_test_scaled
        self.y_train = y_train
        self.y_test = y_test
        self.scaler = scaler
        
        print(f"\n✓ Data prepared")
        print(f"   • Training set: {len(X_train)} samples")
        print(f"   • Test set: {len(X_test)} samples")
        print(f"   • Training set - Active: {sum(y_train == 0)}, Churned: {sum(y_train == 1)}")
        print(f"   • Test set - Active: {sum(y_test == 0)}, Churned: {sum(y_test == 1)}")
    
    def train_model(self, n_estimators=100, max_depth=15, random_state=42):
        """Train Random Forest classifier"""
        self.print_header("MODEL TRAINING")
        
        print(f"\n🤖 Training Random Forest Classifier")
        print(f"   • n_estimators: {n_estimators}")
        print(f"   • max_depth: {max_depth}")
        
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        self.model.fit(self.X_train, self.y_train)
        
        print(f"\n✓ Model trained successfully!")
        
        # Feature importance
        print(f"\n📊 Feature Importance:")
        feature_importance = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': self.model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        for idx, row in feature_importance.iterrows():
            print(f"   {row['Feature']:20s}: {row['Importance']:.4f} {'█' * int(row['Importance'] * 100)}")
    
    def evaluate_model(self):
        """Evaluate model performance"""
        self.print_header("MODEL EVALUATION")
        
        # Predictions
        y_pred_train = self.model.predict(self.X_train)
        y_pred_test = self.model.predict(self.X_test)
        
        y_pred_proba_test = self.model.predict_proba(self.X_test)[:, 1]
        
        # Training metrics
        print(f"\n📊 TRAINING SET METRICS:")
        train_acc = accuracy_score(self.y_train, y_pred_train)
        train_precision = precision_score(self.y_train, y_pred_train, zero_division=0)
        train_recall = recall_score(self.y_train, y_pred_train, zero_division=0)
        train_f1 = f1_score(self.y_train, y_pred_train, zero_division=0)
        
        print(f"   • Accuracy:  {train_acc:.4f} ({train_acc*100:.2f}%)")
        print(f"   • Precision: {train_precision:.4f}")
        print(f"   • Recall:    {train_recall:.4f}")
        print(f"   • F1-Score:  {train_f1:.4f}")
        
        # Testing metrics
        print(f"\n📊 TEST SET METRICS:")
        test_acc = accuracy_score(self.y_test, y_pred_test)
        test_precision = precision_score(self.y_test, y_pred_test, zero_division=0)
        test_recall = recall_score(self.y_test, y_pred_test, zero_division=0)
        test_f1 = f1_score(self.y_test, y_pred_test, zero_division=0)
        roc_auc = roc_auc_score(self.y_test, y_pred_proba_test)
        
        print(f"   • Accuracy:  {test_acc:.4f} ({test_acc*100:.2f}%)")
        print(f"   • Precision: {test_precision:.4f}")
        print(f"   • Recall:    {test_recall:.4f}")
        print(f"   • F1-Score:  {test_f1:.4f}")
        print(f"   • ROC-AUC:   {roc_auc:.4f}")
        
        # Confusion matrix
        print(f"\n📊 CONFUSION MATRIX (Test Set):")
        cm = confusion_matrix(self.y_test, y_pred_test)
        print(f"   {'':20s} Predicted")
        print(f"   {'':20s} Negative  Positive")
        print(f"   Actual Negative  {cm[0,0]:6d}    {cm[0,1]:6d}")
        print(f"   Actual Positive  {cm[1,0]:6d}    {cm[1,1]:6d}")
        
        # Detailed analysis
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        print(f"\n📈 ADDITIONAL METRICS:")
        print(f"   • True Negatives:  {tn}")
        print(f"   • False Positives: {fp}")
        print(f"   • False Negatives: {fn}")
        print(f"   • True Positives:  {tp}")
        print(f"   • Specificity:     {specificity:.4f}")
        print(f"   • Sensitivity:     {sensitivity:.4f}")
        
        # Store metrics for visualization
        return {
            'y_pred_test': y_pred_test,
            'y_pred_proba_test': y_pred_proba_test,
            'test_acc': test_acc,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_f1': test_f1,
            'roc_auc': roc_auc,
            'cm': cm
        }
    
    def visualize_results(self, metrics):
        """Create evaluation visualizations"""
        print("\n" + "="*80)
        print("📊 CREATING VISUALIZATIONS")
        print("="*80)
        
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Confusion Matrix
        ax1 = plt.subplot(2, 3, 1)
        cm = metrics['cm']
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1,
                   xticklabels=['Active', 'Churned'],
                   yticklabels=['Active', 'Churned'])
        ax1.set_title('Confusion Matrix', fontweight='bold')
        ax1.set_ylabel('Actual')
        ax1.set_xlabel('Predicted')
        
        # 2. Metrics comparison
        ax2 = plt.subplot(2, 3, 2)
        metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        metrics_values = [
            metrics['test_acc'],
            metrics['test_precision'],
            metrics['test_recall'],
            metrics['test_f1']
        ]
        colors = plt.cm.viridis(np.linspace(0, 1, len(metrics_names)))
        ax2.bar(metrics_names, metrics_values, color=colors)
        ax2.set_ylabel('Score')
        ax2.set_title('Model Performance Metrics', fontweight='bold')
        ax2.set_ylim([0, 1])
        ax2.grid(True, alpha=0.3, axis='y')
        for i, v in enumerate(metrics_values):
            ax2.text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold')
        
        # 3. ROC Curve
        ax3 = plt.subplot(2, 3, 3)
        fpr, tpr, _ = roc_curve(self.y_test, metrics['y_pred_proba_test'])
        ax3.plot(fpr, tpr, color='#e74c3c', lw=2,
                label=f"ROC curve (AUC = {metrics['roc_auc']:.3f})")
        ax3.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Random')
        ax3.set_xlabel('False Positive Rate')
        ax3.set_ylabel('True Positive Rate')
        ax3.set_title('ROC Curve', fontweight='bold')
        ax3.legend(loc='lower right')
        ax3.grid(True, alpha=0.3)
        
        # 4. Prediction distribution
        ax4 = plt.subplot(2, 3, 4)
        ax4.hist(metrics['y_pred_proba_test'][self.y_test == 0], 
                bins=30, alpha=0.6, label='Active Customers', color='#2ecc71')
        ax4.hist(metrics['y_pred_proba_test'][self.y_test == 1], 
                bins=30, alpha=0.6, label='Churned Customers', color='#e74c3c')
        ax4.set_xlabel('Churn Probability')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Churn Probability Distribution', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. Feature importance
        ax5 = plt.subplot(2, 3, 5)
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[-10:]
        ax5.barh(range(len(indices)), importances[indices],
                color=plt.cm.plasma(np.linspace(0, 1, len(indices))))
        ax5.set_yticks(range(len(indices)))
        ax5.set_yticklabels([self.feature_names[i] for i in indices])
        ax5.set_xlabel('Importance')
        ax5.set_title('Top 10 Feature Importance', fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='x')
        
        # 6. Class distribution
        ax6 = plt.subplot(2, 3, 6)
        class_counts = [sum(self.y_test == 0), sum(self.y_test == 1)]
        ax6.pie(class_counts, labels=['Active', 'Churned'], autopct='%1.1f%%',
               colors=['#2ecc71', '#e74c3c'], startangle=90)
        ax6.set_title('Test Set Class Distribution', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('outputs/11_churn_prediction_model.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/11_churn_prediction_model.png")
        plt.close()
    
    def predict_churn(self, features_df):
        """Predict churn for customers"""
        print("\n" + "="*80)
        print("🔮 CHURN PREDICTIONS")
        print("="*80)
        
        X = features_df[self.feature_names].values
        X_scaled = self.scaler.transform(X)
        
        churn_proba = self.model.predict_proba(X_scaled)[:, 1]
        features_df['ChurnProbability'] = churn_proba
        features_df['ChurnRisk'] = pd.cut(
            churn_proba,
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        
        print(f"\n✓ Predictions generated for {len(features_df):,} customers")
        print(f"\n📊 Risk Distribution:")
        risk_dist = features_df['ChurnRisk'].value_counts()
        for risk, count in risk_dist.items():
            print(f"   • {risk}: {count:,} customers ({count/len(features_df)*100:.1f}%)")
        
        # High-risk customers
        print(f"\n⚠️  HIGH-RISK CUSTOMERS (Top 20):")
        high_risk = features_df.nlargest(20, 'ChurnProbability')[
            ['CustomerID', 'Recency', 'Frequency', 'TotalMonetary', 'ChurnProbability', 'ChurnRisk']
        ]
        for idx, row in high_risk.iterrows():
            print(f"   Customer {int(row['CustomerID']):6d}: "
                  f"Prob={row['ChurnProbability']:.2%}, "
                  f"Risk={row['ChurnRisk']:12s}, "
                  f"Recency={int(row['Recency']):3d} days, "
                  f"Spent=£{row['TotalMonetary']:,.0f}")
        
        return features_df
    
    def save_model(self):
        """Save trained model"""
        print("\n" + "="*80)
        print("💾 SAVING MODEL")
        print("="*80)
        
        model_path = 'outputs/churn_model.pkl'
        scaler_path = 'outputs/churn_scaler.pkl'
        
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"✓ Model saved: {model_path}")
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"✓ Scaler saved: {scaler_path}")
    
    def run_complete_churn_prediction(self):
        """Execute complete churn prediction pipeline"""
        print("\n" + "="*80)
        print("🚀 MODULE 7: AI-BASED CHURN PREDICTION")
        print("="*80)
        
        # Define churn
        churn_df = self.define_churn_label(churn_days=90)
        
        # Create features
        features_df = self.create_features(churn_df, churn_days=90)
        
        # Prepare data
        self.prepare_data(features_df)
        
        # Train model
        self.train_model(n_estimators=100, max_depth=15)
        
        # Evaluate
        metrics = self.evaluate_model()
        
        # Visualize
        self.visualize_results(metrics)
        
        # Predict
        predictions_df = self.predict_churn(features_df)
        
        # Save model
        self.save_model()
        
        # Save predictions
        predictions_df.to_csv('outputs/churn_predictions.csv', index=False)
        print("✓ Predictions saved: outputs/churn_predictions.csv")
        
        print("\n" + "="*80)
        print("✅ CHURN PREDICTION COMPLETE!")
        print("="*80)
        
        return predictions_df


def main():
    """Main execution"""
    model = ChurnPredictionModel(
        'outputs/online_retail_cleaned.csv',
        'outputs/rfm_analysis.csv'
    )
    model.run_complete_churn_prediction()


if __name__ == "__main__":
    main()
