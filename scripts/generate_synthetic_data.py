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
import hashlib

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
            'relationship_types': ['Owner', 'Partner', 'Manager', 'Director', 'Shareholder', 'Agent'],  # Default values if not in pattern file
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
    synthetic['emirate_name_en'] = np.random.choice(patterns['emirate'], size=sample_size)
    synthetic['emirate_name_ar'] = synthetic['emirate_name_en'].map({
        'Dubai': 'دبي',
        'Abu Dhabi': 'أبو ظبي',
        'Sharjah': 'الشارقة',
        'Ajman': 'عجمان',
        'Ras Al Khaimah': 'رأس الخيمة',
        'Fujairah': 'الفجيرة',
        'Umm Al Quwain': 'أم القيوين'
    })
    
    # Authority based on emirate using the mapping
    synthetic['issuance_authority_en'] = synthetic['emirate_name_en'].apply(
        lambda x: np.random.choice(patterns['emirate_authorities'][x])
    )
    
    # Business names
    synthetic['bl_name_en'] = [
        f"{fake_en.company()} {random.choice(['LLC', 'Trading', 'Services', 'International', 'Group', 'FZ-LLC', 'DMCC'])}"
        for _ in range(sample_size)
    ]
    synthetic['bl_name_ar'] = [
        get_display(reshaper.reshape(f"شركة {fake_ar.company()}"))
        for _ in range(sample_size)
    ]
    
    # License numbers
    synthetic['bl'] = [f"BL-{random.randint(100000, 999999)}" for _ in range(sample_size)]
    synthetic['bl_cbls'] = [f"CBLS-{random.randint(10000, 99999)}" for _ in range(sample_size)]
    
    # Dates
    today = pd.Timestamp.now()
    synthetic['bl_est_date'] = [
        (today - pd.Timedelta(days=random.randint(0, 3650))).strftime('%d/%m/%Y')
        for _ in range(sample_size)
    ]
    synthetic['bl_exp_date'] = [
        (pd.Timestamp(d) + pd.Timedelta(days=random.randint(365, 1095))).strftime('%d/%m/%Y')
        for d in synthetic['bl_est_date']
    ]
    
    # Status and types
    synthetic['bl_status_en'] = np.random.choice(patterns['status'], size=sample_size)
    synthetic['bl_legal_type_en'] = np.random.choice(patterns['legal_type'], size=sample_size)
    synthetic['bl_type_en'] = np.random.choice(patterns['license_type'], size=sample_size)
    
    # Business activities
    activities = patterns['business_codes'].sample(n=sample_size, replace=True)
    synthetic['business_activity_code'] = activities['Business Activity Code'].values
    synthetic['business_activity_desc_en'] = activities['Business Activity Desc En'].values
    synthetic['business_activity_desc_ar'] = activities['Business Activity Desc Ar'].values
    
    # Owner information
    synthetic['owner_nationality_en'] = np.random.choice(patterns['nationalities'], size=sample_size)
    synthetic['owner_gender'] = np.random.choice(patterns['genders'], size=sample_size)
    synthetic['relationship_type_en'] = np.random.choice(patterns['relationship_types'], size=sample_size)
    
    # Addresses and coordinates (based on emirate)
    coords = {
        'Dubai': (25.2048, 55.2708),
        'Abu Dhabi': (24.4539, 54.3773),
        'Sharjah': (25.3463, 55.4209),
        'Ajman': (25.4052, 55.5136),
        'Ras Al Khaimah': (25.7895, 55.9432),
        'Fujairah': (25.1288, 56.3265),
        'Umm Al Quwain': (25.0000, 55.0000)  # Fixed coordinates
    }
    
    synthetic['bl_full_address'] = synthetic.apply(
        lambda row: f"Unit {random.randint(100,999)}, {fake_en.street_address()}, {row['emirate_name_en']}", 
        axis=1
    )
    
    # Generate license_pk using md5 hash of issuance_authority_en and bl
    synthetic['license_pk'] = synthetic.apply(
        lambda row: hashlib.md5(f"{row['issuance_authority_en']}|{row['bl']}".encode()).hexdigest(),
        axis=1
    )
    
    # Ensure columns are in the correct order
    column_order = [
        'license_pk',
        'emirate_name_en',
        'emirate_name_ar',
        'issuance_authority_en',
        'bl_name_en',
        'bl_name_ar',
        'bl',
        'bl_cbls',
        'bl_est_date',
        'bl_exp_date',
        'bl_status_en',
        'bl_legal_type_en',
        'bl_type_en',
        'business_activity_code',
        'business_activity_desc_en',
        'business_activity_desc_ar',
        'owner_nationality_en',
        'owner_gender',
        'relationship_type_en',
        'bl_full_address',
        'license_latitude',
        'license_longitude'
    ]
    
    # Add coordinates at the end
    synthetic['license_latitude'] = synthetic['emirate_name_en'].apply(
        lambda x: f"{coords.get(x, (25.0, 55.0))[0]}°N"  # Format as DMS
    )
    synthetic['license_longitude'] = synthetic['emirate_name_en'].apply(
        lambda x: f"{coords.get(x, (25.0, 55.0))[1]}°E"  # Format as DMS
    )
    
    synthetic = synthetic[column_order]
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