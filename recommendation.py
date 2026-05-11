"""
MODULE 9 - AI RECOMMENDATION SYSTEM
====================================
Product recommendation system using Apriori algorithm and market basket analysis.

Identifies:
- Products frequently bought together
- Association rules
- Support, Confidence, Lift metrics

Generates:
- Personalized recommendations
- Cross-sell opportunities
- Bundle suggestions
"""

import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

try:
    from mlxtend.frequent_patterns import apriori, association_rules
    from mlxtend.preprocessing import TransactionEncoder
    HAS_MLXTEND = True
except ImportError:
    HAS_MLXTEND = False


class RecommendationEngine:
    """Product recommendation system"""
    
    def __init__(self, cleaned_data_path):
        self.df = pd.read_csv(cleaned_data_path)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.transactions = None
        self.frequent_itemsets = None
        self.rules = None
        
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"🎁 {title}")
        print("="*80)
    
    def prepare_transactions(self):
        """Prepare transaction data for market basket analysis"""
        self.print_header("PREPARING TRANSACTION DATA")
        
        # Group by invoice to get products per transaction
        transactions_list = []
        
        for invoice_no in self.df['InvoiceNo'].unique():
            invoice_data = self.df[self.df['InvoiceNo'] == invoice_no]
            products = invoice_data['Description'].unique().tolist()
            transactions_list.append(products)
        
        print(f"\n✓ Prepared {len(transactions_list):,} transactions")
        print(f"   • Unique Products: {self.df['Description'].nunique():,}")
        print(f"   • Average Items per Transaction: {sum(len(t) for t in transactions_list) / len(transactions_list):.2f}")
        
        self.transactions = transactions_list
        return transactions_list
    
    def apply_apriori_algorithm(self, min_support=0.01, min_confidence=0.3):
        """Apply Apriori algorithm for frequent itemsets"""
        if not HAS_MLXTEND:
            print("\n⚠️  MLXtend library not available. Using alternative approach.")
            return self.apply_simple_association_rules()
        
        self.print_header("APRIORI ALGORITHM")
        
        print(f"\n📊 Algorithm Parameters:")
        print(f"   • Minimum Support: {min_support*100:.1f}%")
        print(f"   • Minimum Confidence: {min_confidence*100:.1f}%")
        
        # Prepare data for mlxtend
        te = TransactionEncoder()
        te_ary = te.fit(self.transactions).transform(self.transactions)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        
        # Find frequent itemsets
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        
        print(f"\n✓ Found {len(frequent_itemsets)} frequent itemsets")
        
        if len(frequent_itemsets) > 1:
            # Generate association rules
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
            
            if len(rules) > 0:
                rules['antecedent_str'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
                rules['consequent_str'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
                rules = rules.sort_values('lift', ascending=False)
                
                print(f"✓ Generated {len(rules)} association rules")
                
                self.frequent_itemsets = frequent_itemsets
                self.rules = rules
                
                return rules
        
        print("⚠️  Insufficient frequent itemsets for rule generation")
        return None
    
    def apply_simple_association_rules(self):
        """Apply simple association rule mining without mlxtend"""
        self.print_header("MARKET BASKET ANALYSIS (Simple Method)")
        
        print(f"\n📊 Analyzing {len(self.transactions)} transactions...")
        
        # Count co-occurrences
        co_occurrences = defaultdict(int)
        product_counts = defaultdict(int)
        total_transactions = len(self.transactions)
        
        for transaction in self.transactions:
            # Count individual products
            for product in transaction:
                product_counts[product] += 1
            
            # Count co-occurrences
            if len(transaction) >= 2:
                for pair in combinations(sorted(transaction), 2):
                    co_occurrences[pair] += 1
        
        # Generate rules
        rules_list = []
        
        for (product_a, product_b), count in sorted(
            co_occurrences.items(),
            key=lambda x: x[1],
            reverse=True
        )[:50]:  # Top 50 rules
            
            support = count / total_transactions
            if support < 0.01:  # Skip low support
                continue
            
            # Confidence: P(B|A) = P(A,B) / P(A)
            confidence_ab = count / product_counts[product_a]
            confidence_ba = count / product_counts[product_b]
            
            # Lift
            support_a = product_counts[product_a] / total_transactions
            support_b = product_counts[product_b] / total_transactions
            lift_ab = confidence_ab / support_b if support_b > 0 else 0
            
            if confidence_ab >= 0.3 or confidence_ba >= 0.3:
                rules_list.append({
                    'Antecedent': product_a,
                    'Consequent': product_b,
                    'Support': support,
                    'Confidence_AB': confidence_ab,
                    'Lift_AB': lift_ab,
                    'Count': count
                })
                
                rules_list.append({
                    'Antecedent': product_b,
                    'Consequent': product_a,
                    'Support': support,
                    'Confidence_AB': confidence_ba,
                    'Lift_AB': (confidence_ba / support_a) if support_a > 0 else 0,
                    'Count': count
                })
        
        rules_df = pd.DataFrame(rules_list)
        if len(rules_df) > 0:
            rules_df = rules_df.drop_duplicates().sort_values('Lift_AB', ascending=False)
            self.rules = rules_df
            
            print(f"✓ Generated {len(rules_df)} association rules")
            return rules_df
        
        return None
    
    def display_association_rules(self):
        """Display top association rules"""
        if self.rules is None or len(self.rules) == 0:
            print("\n⚠️  No association rules found")
            return
        
        self.print_header("TOP ASSOCIATION RULES")
        
        # Display rules
        if 'antecedent_str' in self.rules.columns:
            # MLXtend format
            top_rules = self.rules.head(15)
            print(f"\n{'Antecedent':<40} => {'Consequent':<40} | Support | Confidence | Lift")
            print("─" * 110)
            
            for _, rule in top_rules.iterrows():
                print(f"{str(rule['antecedent_str']):<40} => {str(rule['consequent_str']):<40} | "
                      f"{rule['support']:>7.3f} | {rule['confidence']:>10.3f} | {rule['lift']:>4.2f}")
        else:
            # Simple format
            top_rules = self.rules.head(15)
            print(f"\n{'Antecedent':<40} => {'Consequent':<40} | Support | Confidence | Lift")
            print("─" * 110)
            
            for _, rule in top_rules.iterrows():
                ant_str = str(rule['Antecedent'])[:39]
                cons_str = str(rule['Consequent'])[:39]
                print(f"{ant_str:<40} => {cons_str:<40} | "
                      f"{rule['Support']:>7.3f} | {rule['Confidence_AB']:>10.3f} | {rule['Lift_AB']:>4.2f}")
    
    def get_recommendations(self, product_name, top_n=5):
        """Get product recommendations for a specific product"""
        if self.rules is None:
            return []
        
        if 'antecedent_str' in self.rules.columns:
            # MLXtend format
            matching_rules = self.rules[
                self.rules['antecedents'].apply(lambda x: product_name in x)
            ].nlargest(top_n, 'lift')
            
            recommendations = []
            for _, rule in matching_rules.iterrows():
                consequent = list(rule['consequents'])[0] if len(rule['consequents']) > 0 else None
                if consequent:
                    recommendations.append({
                        'Product': consequent,
                        'Lift': rule['lift'],
                        'Confidence': rule['confidence'],
                        'Support': rule['support']
                    })
        else:
            # Simple format
            matching_rules = self.rules[
                self.rules['Antecedent'].str.contains(product_name, na=False)
            ].nlargest(top_n, 'Lift_AB')
            
            recommendations = []
            for _, rule in matching_rules.iterrows():
                recommendations.append({
                    'Product': rule['Consequent'],
                    'Lift': rule['Lift_AB'],
                    'Confidence': rule['Confidence_AB'],
                    'Support': rule['Support']
                })
        
        return recommendations
    
    def generate_customer_recommendations(self, customer_purchase_history, top_n=5):
        """Generate personalized recommendations for a customer"""
        print(f"\n👥 Personalized Recommendations:")
        
        recommendations_dict = {}
        
        for product in customer_purchase_history:
            recs = self.get_recommendations(product, top_n)
            for rec in recs:
                prod_name = rec['Product']
                if prod_name not in recommendations_dict:
                    recommendations_dict[prod_name] = []
                recommendations_dict[prod_name].append(rec['Lift'])
        
        # Score recommendations
        scored_recs = [
            (prod, np.mean(scores))
            for prod, scores in recommendations_dict.items()
        ]
        scored_recs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n   Based on your purchase of: {', '.join(customer_purchase_history[:3])}")
        print(f"\n   We recommend:")
        for idx, (product, score) in enumerate(scored_recs[:5], 1):
            print(f"   {idx}. {product[:60]:60s} (Score: {score:.2f})")
        
        return scored_recs
    
    def visualize_rules(self):
        """Visualize top association rules"""
        if self.rules is None or len(self.rules) == 0:
            print("\n⚠️  No rules to visualize")
            return
        
        print("\n📊 Creating visualizations...")
        
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Prepare data
        if 'antecedent_str' in self.rules.columns:
            top_rules = self.rules.head(10)
            support_vals = top_rules['support'].values
            confidence_vals = top_rules['confidence'].values
            lift_vals = top_rules['lift'].values
            labels = [f"{str(list(x)[0])[:20]}" for x in top_rules['antecedents']]
        else:
            top_rules = self.rules.head(10)
            support_vals = top_rules['Support'].values
            confidence_vals = top_rules['Confidence_AB'].values
            lift_vals = top_rules['Lift_AB'].values
            labels = [str(x)[:20] for x in top_rules['Antecedent']]
        
        # 1. Support bar chart
        axes[0, 0].barh(range(len(support_vals)), support_vals, color='#3498db')
        axes[0, 0].set_yticks(range(len(labels)))
        axes[0, 0].set_yticklabels(labels, fontsize=8)
        axes[0, 0].set_xlabel('Support')
        axes[0, 0].set_title('Support of Top 10 Rules', fontweight='bold')
        axes[0, 0].invert_yaxis()
        
        # 2. Confidence bar chart
        axes[0, 1].barh(range(len(confidence_vals)), confidence_vals, color='#2ecc71')
        axes[0, 1].set_yticks(range(len(labels)))
        axes[0, 1].set_yticklabels(labels, fontsize=8)
        axes[0, 1].set_xlabel('Confidence')
        axes[0, 1].set_title('Confidence of Top 10 Rules', fontweight='bold')
        axes[0, 1].invert_yaxis()
        
        # 3. Lift bar chart
        axes[1, 0].barh(range(len(lift_vals)), lift_vals, color='#e74c3c')
        axes[1, 0].set_yticks(range(len(labels)))
        axes[1, 0].set_yticklabels(labels, fontsize=8)
        axes[1, 0].set_xlabel('Lift')
        axes[1, 0].set_title('Lift of Top 10 Rules', fontweight='bold')
        axes[1, 0].invert_yaxis()
        
        # 4. Scatter: Support vs Confidence vs Lift
        scatter = axes[1, 1].scatter(support_vals, confidence_vals, s=lift_vals*100, 
                                    c=lift_vals, cmap='viridis', alpha=0.6)
        axes[1, 1].set_xlabel('Support')
        axes[1, 1].set_ylabel('Confidence')
        axes[1, 1].set_title('Support vs Confidence (size=Lift)', fontweight='bold')
        plt.colorbar(scatter, ax=axes[1, 1], label='Lift')
        
        plt.tight_layout()
        plt.savefig('outputs/12_recommendation_rules.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/12_recommendation_rules.png")
        plt.close()
    
    def save_rules(self):
        """Save association rules"""
        if self.rules is not None and len(self.rules) > 0:
            self.rules.to_csv('outputs/association_rules.csv', index=False)
            print("✓ Saved: outputs/association_rules.csv")
    
    def run_complete_recommendation_system(self):
        """Execute complete recommendation system"""
        print("\n" + "="*80)
        print("🚀 MODULE 9: AI RECOMMENDATION SYSTEM")
        print("="*80)
        
        # Prepare transactions
        self.prepare_transactions()
        
        # Apply Apriori
        rules = self.apply_apriori_algorithm(min_support=0.01, min_confidence=0.25)
        
        if rules is not None:
            # Display rules
            self.display_association_rules()
            
            # Example recommendations
            print("\n" + "="*80)
            print("📌 EXAMPLE CUSTOMER RECOMMENDATIONS")
            print("="*80)
            
            # Get a sample customer's purchases
            sample_customer = self.df.groupby('CustomerID')['Description'].apply(list).iloc[0]
            self.generate_customer_recommendations(sample_customer[:3], top_n=5)
            
            # Visualize
            self.visualize_rules()
            
            # Save rules
            self.save_rules()
        
        print("\n" + "="*80)
        print("✅ RECOMMENDATION SYSTEM COMPLETE!")
        print("="*80)


def main():
    """Main execution"""
    engine = RecommendationEngine('outputs/online_retail_cleaned.csv')
    engine.run_complete_recommendation_system()


if __name__ == "__main__":
    main()
