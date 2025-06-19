#!/usr/bin/env python3

import pandas as pd
import numpy as np
from faker import Faker
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display
import random
import argparse
from pathlib import Path
import sys

def load_patterns(pattern_file):
    """Load real data patterns to maintain distributions."""
    try:
        # Set low_memory=False to handle mixed types
        df = pd.read_csv(pattern_file, sep='|', low_memory=False)
        
        # Create emirate to authority mapping
        emirate_authorities = {}
        for emirate in df['Emirate Name En'].unique():
            authorities = df[df['Emirate Name En'] == emirate]['Issuance Authority En'].unique()
            emirate_authorities[emirate] = authorities if len(authorities) > 0 else ['Default Authority']
        
        patterns = {
            'emirate': df['Emirate Name En'].unique(),
            'emirate_authorities': emirate_authorities,
            'status': df['BL Status EN'].unique(),
            'legal_type': df['BL Legal Type En'].unique(),
            'license_type': df['BL Type En'].unique(),
            'business_codes': df[['Business Activity Code', 'Business Activity Desc En', 'Business Activity Desc Ar']].drop_duplicates(),
            'relationship_types': df['Relationship Type En'].unique(),
            'nationalities': df['Owner Nationality En'].unique(),
            'genders': df['Owner Gender'].unique()
        }
        return patterns
    except Exception as e:
        print(f"Error loading pattern file: {e}", file=sys.stderr)
        sys.exit(1)

def generate_synthetic_licenses(patterns, sample_size=1000):
    """Generate synthetic license data maintaining real patterns."""
    fake_en = Faker()
    fake_ar = Faker('ar_AA')
    reshaper = ArabicReshaper()
    
    # Initialize empty DataFrame
    synthetic = pd.DataFrame()
    
    # Generate data maintaining distributions
    synthetic['Emirate Name En'] = np.random.choice(patterns['emirate'], size=sample_size)
    synthetic['Emirate Name Ar'] = synthetic['Emirate Name En'].map({
        'Dubai': 'دبي',
        'Abu Dhabi': 'أبو ظبي',
        'Sharjah': 'الشارقة',
        'Ajman': 'عجمان',
        'Ras Al Khaimah': 'رأس الخيمة',
        'Fujairah': 'الفجيرة',
        'Umm Al Quwain': 'أم القيوين'
    })
    
    # Authority based on emirate using the mapping
    synthetic['Issuance Authority En'] = synthetic['Emirate Name En'].apply(
        lambda x: np.random.choice(patterns['emirate_authorities'][x])
    )
    
    # Business names
    synthetic['BL Name En'] = [
        f"{fake_en.company()} {random.choice(['LLC', 'Trading', 'Services', 'International', 'Group', 'FZ-LLC', 'DMCC'])}"
        for _ in range(sample_size)
    ]
    synthetic['BL Name Ar'] = [
        get_display(reshaper.reshape(f"شركة {fake_ar.company()}"))
        for _ in range(sample_size)
    ]
    
    # License numbers
    synthetic['BL #'] = [f"BL-{random.randint(100000, 999999)}" for _ in range(sample_size)]
    synthetic['BL CBLS #'] = [f"CBLS-{random.randint(10000, 99999)}" for _ in range(sample_size)]
    
    # Dates
    today = pd.Timestamp.now()
    synthetic['BL Est Date'] = [
        (today - pd.Timedelta(days=random.randint(0, 3650))).strftime('%d/%m/%Y')
        for _ in range(sample_size)
    ]
    synthetic['BL Exp Date'] = [
        (pd.Timestamp(d) + pd.Timedelta(days=random.randint(365, 1095))).strftime('%d/%m/%Y')
        for d in synthetic['BL Est Date']
    ]
    
    # Status and types
    synthetic['BL Status EN'] = np.random.choice(patterns['status'], size=sample_size)
    synthetic['BL Legal Type En'] = np.random.choice(patterns['legal_type'], size=sample_size)
    synthetic['BL Type En'] = np.random.choice(patterns['license_type'], size=sample_size)
    
    # Business activities
    activities = patterns['business_codes'].sample(n=sample_size, replace=True)
    synthetic['Business Activity Code'] = activities['Business Activity Code'].values
    synthetic['Business Activity Desc En'] = activities['Business Activity Desc En'].values
    synthetic['Business Activity Desc Ar'] = activities['Business Activity Desc Ar'].values
    
    # Owner information
    synthetic['Owner Nationality En'] = np.random.choice(patterns['nationalities'], size=sample_size)
    synthetic['Owner Gender'] = np.random.choice(patterns['genders'], size=sample_size)
    
    # Addresses and coordinates (based on emirate)
    coords = {
        'Dubai': (25.2048, 55.2708),
        'Abu Dhabi': (24.4539, 54.3773),
        'Sharjah': (25.3463, 55.4209),
        'Ajman': (25.4052, 55.5136),
        'Ras Al Khaimah': (25.7895, 55.9432),
        'Fujairah': (25.1288, 56.3265),
        'Umm Al Quwain': (25.5647, 55.5532)
    }
    
    synthetic['BL Full Address'] = synthetic.apply(
        lambda row: f"Unit {random.randint(100,999)}, {fake_en.street_address()}, {row['Emirate Name En']}", 
        axis=1
    )
    
    synthetic['License Latitude'] = synthetic['Emirate Name En'].apply(
        lambda x: coords.get(x, (25.0, 55.0))[0] + np.random.normal(0, 0.01)
    )
    synthetic['License Longitude'] = synthetic['Emirate Name En'].apply(
        lambda x: coords.get(x, (25.0, 55.0))[1] + np.random.normal(0, 0.01)
    )
    
    return synthetic

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic UAE business license data')
    parser.add_argument('--pattern-file', type=str, required=True,
                      help='Path to real data file to extract patterns from')
    parser.add_argument('--output', type=str, required=True,
                      help='Output file path (CSV)')
    parser.add_argument('--sample-size', type=int, default=1000,
                      help='Number of synthetic records to generate')
    
    args = parser.parse_args()
    
    print(f"Loading patterns from {args.pattern_file}...")
    patterns = load_patterns(args.pattern_file)
    
    print(f"Generating {args.sample_size} synthetic records...")
    synthetic = generate_synthetic_licenses(patterns, args.sample_size)
    
    print(f"Saving to {args.output}...")
    synthetic.to_csv(args.output, sep='|', index=False)
    print("Done!")

if __name__ == '__main__':
    main() 