import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_analyze_data():
    """Load and analyze the matches dataset"""
    
    # Load the data
    df = pd.read_csv('data_matches - dataset.csv')
    
    print("=== DATASET OVERVIEW ===")
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())
    
    print("\n=== DATA QUALITY CHECK ===")
    print(f"Missing values:\n{df.isnull().sum()}")
    print(f"\nData types:\n{df.dtypes}")
    
    print("\n=== BASIC STATISTICS ===")
    print(f"Total unique items in ITEM_A: {df['ITEM_A'].nunique()}")
    print(f"Total unique items in ITEM_B: {df['ITEM_B'].nunique()}")
    print(f"Total unique items overall: {pd.concat([df['ITEM_A'], df['ITEM_B']]).nunique()}")
    
    # Check for self-matches
    self_matches = df[df['ITEM_A'] == df['ITEM_B']]
    print(f"\nSelf-matches (ITEM_A == ITEM_B): {len(self_matches)}")
    if len(self_matches) > 0:
        print("Self-matches found:")
        print(self_matches)
    
    # Analyze title similarities
    print("\n=== TITLE ANALYSIS ===")
    
    # Check for exact title matches
    exact_title_matches = df[df['TITLE_A'] == df['TITLE_B']]
    print(f"Exact title matches: {len(exact_title_matches)}")
    
    # Check for partial title matches
    partial_matches = []
    for idx, row in df.iterrows():
        title_a = str(row['TITLE_A']).lower()
        title_b = str(row['TITLE_B']).lower()
        
        # Check if words overlap
        words_a = set(title_a.split())
        words_b = set(title_b.split())
        common_words = words_a.intersection(words_b)
        
        if len(common_words) > 0 and len(common_words) >= min(len(words_a), len(words_b)) * 0.3:
            partial_matches.append({
                'ITEM_A': row['ITEM_A'],
                'TITLE_A': row['TITLE_A'],
                'ITEM_B': row['ITEM_B'],
                'TITLE_B': row['TITLE_B'],
                'common_words': len(common_words)
            })
    
    print(f"Partial title matches (30%+ word overlap): {len(partial_matches)}")
    
    # Show some examples of partial matches
    if partial_matches:
        print("\nExamples of partial matches:")
        for match in partial_matches[:5]:
            print(f"  {match['TITLE_A']} <-> {match['TITLE_B']} (common words: {match['common_words']})")
    
    return df

def create_visualizations(df):
    """Create basic visualizations for the data"""
    
    # Create a simple visualization of item frequency
    all_items = pd.concat([df['ITEM_A'], df['ITEM_B']])
    item_counts = all_items.value_counts()
    
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    item_counts.head(10).plot(kind='bar')
    plt.title('Top 10 Most Frequent Items')
    plt.xticks(rotation=45)
    plt.ylabel('Frequency')
    
    # Title length distribution
    df['TITLE_A_LENGTH'] = df['TITLE_A'].str.len()
    df['TITLE_B_LENGTH'] = df['TITLE_B'].str.len()
    
    plt.subplot(1, 2, 2)
    plt.hist([df['TITLE_A_LENGTH'], df['TITLE_B_LENGTH']], 
             label=['Title A', 'Title B'], alpha=0.7, bins=20)
    plt.title('Title Length Distribution')
    plt.xlabel('Title Length (characters)')
    plt.ylabel('Frequency')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('data_analysis_plots.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n=== VISUALIZATION CREATED ===")
    print("Saved 'data_analysis_plots.png' with basic data visualizations")

if __name__ == "__main__":
    # Load and analyze the data
    df = load_and_analyze_data()
    
    # Create visualizations
    create_visualizations(df)
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("The script has analyzed the matches dataset and created visualizations.")
    print("Please check the generated 'data_analysis_plots.png' file for charts.") 