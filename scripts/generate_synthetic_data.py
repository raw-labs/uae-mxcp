#!/usr/bin/env python3
"""
A simple, Faker-based synthetic data generator for UAE business licenses.
This script generates data based on pre-defined, realistic data profiles
and distributions, without needing a source pattern file.
"""
import pandas as pd
import numpy as np
from faker import Faker
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display
import random
import argparse
from pathlib import Path
import hashlib
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generates synthetic UAE business license data using Faker and pre-defined distributions."""

    def __init__(self):
        self.fake_en = Faker()
        self.fake_ar = Faker('ar_AA')
        self.reshaper = ArabicReshaper()

        # --- Pre-defined Data Profiles & Distributions ---

        self.emirates = {
            'Dubai': 0.6,
            'Abu Dhabi': 0.2,
            'Sharjah': 0.1,
            'Ajman': 0.04,
            'Ras Al Khaimah': 0.03,
            'Fujairah': 0.02,
            'Umm Al Quwain': 0.01
        }
        self.emirates_ar = {
            'Dubai': 'دبي', 'Abu Dhabi': 'أبو ظبي', 'Sharjah': 'الشارقة',
            'Ajman': 'عجمان', 'Ras Al Khaimah': 'رأس الخيمة', 'Fujairah': 'الفجيرة',
            'Umm Al Quwain': 'أم القيوين'
        }

        self.authorities = {
            'Dubai': {'Department of Economic Development': 0.7, 'Dubai Silicon Oasis Authority': 0.1, 'DMCC': 0.1, 'Dubai South': 0.1},
            'Abu Dhabi': {'Abu Dhabi Department of Economic Development': 0.8, 'ADGM': 0.1, 'KEZAD': 0.1},
            'Sharjah': {'Sharjah Economic Development Department': 0.9, 'Sharjah Publishing City': 0.1},
            'default': {'Department of Economic Development': 0.7, 'Municipality': 0.3}
        }
        self.authorities_ar = {
            'Department of Economic Development': 'دائرة التنمية الاقتصادية',
            'Dubai Silicon Oasis Authority': 'سلطة واحة دبي للسيليكون',
            'DMCC': 'مركز دبي للسلع المتعددة',
            'Dubai South': 'دبي الجنوب',
            'Abu Dhabi Department of Economic Development': 'دائرة التنمية الاقتصادية في أبوظبي',
            'ADGM': 'سوق أبوظبي العالمي',
            'KEZAD': 'مجموعة كيزاد',
            'Sharjah Economic Development Department': 'دائرة التنمية الاقتصادية في الشارقة',
            'Sharjah Publishing City': 'مدينة الشارقة للنشر',
            'Municipality': 'بلدية'
        }

        self.statuses = {'Active': 0.8, 'Expired': 0.15, 'Cancelled': 0.05}
        self.statuses_ar = {'Active': 'نشط', 'Expired': 'منتهي الصلاحية', 'Cancelled': 'ملغاة'}

        self.legal_types = {'LLC': 0.6, 'Sole Establishment': 0.2, 'Civil Company': 0.1, 'Free Zone Establishment': 0.1}
        self.legal_types_ar = {'LLC': 'ذ.م.م', 'Sole Establishment': 'مؤسسة فردية', 'Civil Company': 'شركة مدنية', 'Free Zone Establishment': 'مؤسسة منطقة حرة'}

        self.license_types = {'Commercial': 0.5, 'Professional': 0.4, 'Industrial': 0.1}
        self.license_types_ar = {'Commercial': 'تجاري', 'Professional': 'مهني', 'Industrial': 'صناعي'}

        self.nationalities = {
            'Emirati': 0.3, 'Indian': 0.2, 'Pakistani': 0.1, 'Egyptian': 0.05,
            'British': 0.05, 'Filipino': 0.05, 'Other': 0.25
        }
        self.nationalities_ar = {
            'Emirati': 'إماراتي', 'Indian': 'هندي', 'Pakistani': 'باكستاني', 'Egyptian': 'مصري',
            'British': 'بريطاني', 'Filipino': 'فلبيني', 'Other': 'آخر'
        }

        self.genders = {'Male': 0.7, 'Female': 0.3}
        self.relationship_types = {'Owner': 0.6, 'Partner': 0.3, 'Manager': 0.1}
        self.relationship_types_ar = {'Owner': 'مالك', 'Partner': 'شريك', 'Manager': 'مدير'}

        self.activities = [
            (829900, "Business Support Service Activities", "أنشطة خدمات دعم الأعمال"),
            (477100, "Retail sale of clothing, footwear and textiles", "تجارة التجزئة في الملابس والأحذية والمنسوجات"),
            (620100, "Computer programming activities", "أنشطة برمجة الكمبيوتر"),
            (561000, "Restaurants and mobile food service activities", "المطاعم وأنشطة خدمات الطعام المتنقلة"),
            (702000, "Management consultancy activities", "أنشطة استشارات الإدارة"),
        ]

        self.coordinates = {
            'Dubai': {'lat': (25.0, 25.3), 'long': (55.0, 55.4)},
            'Abu Dhabi': {'lat': (24.2, 24.5), 'long': (54.3, 54.7)},
            'Sharjah': {'lat': (25.3, 25.4), 'long': (55.4, 55.6)},
            'Ajman': {'lat': (25.35, 25.45), 'long': (55.4, 55.55)},
            'Ras Al Khaimah': {'lat': (25.6, 25.8), 'long': (55.9, 56.1)},
            'Fujairah': {'lat': (25.1, 25.2), 'long': (56.3, 56.4)},
            'Umm Al Quwain': {'lat': (25.5, 25.6), 'long': (55.5, 55.7)},
        }

    def _sanitize(self, text: str) -> str:
        """Removes characters that could break the CSV structure."""
        if not isinstance(text, str):
            return text
        return text.replace('|', ' ').replace('\n', ' ').replace('\r', ' ')

    def _choose_weighted(self, choices: dict):
        """Choose an item from a dictionary of choices with weights."""
        return np.random.choice(list(choices.keys()), p=list(choices.values()))

    def _generate_business_name(self, license_type: str) -> tuple:
        """Generate realistic business names in English and Arabic."""
        name = self._sanitize(self.fake_en.company())
        if license_type == 'Commercial':
            suffix = random.choice(['Trading', 'LLC', 'FZE'])
        elif license_type == 'Professional':
            suffix = random.choice(['Consultancy', 'Services', 'Management'])
        else:
            suffix = random.choice(['Industries', 'Manufacturing'])

        en_name = f"{name} {suffix}"
        ar_name = get_display(self.reshaper.reshape(f"شركة {self._sanitize(self.fake_ar.company())} {suffix}"))
        return en_name, ar_name

    def _generate_coordinate(self, emirate: str, coord_type: str) -> str:
        """Generate a random coordinate within the emirate's bounding box."""
        bounds = self.coordinates.get(emirate, self.coordinates['Dubai'])
        lat_min, lat_max = bounds['lat']
        long_min, long_max = bounds['long']

        if coord_type == 'lat':
            val = random.uniform(lat_min, lat_max)
            return f"{val:.4f}°N"
        else:
            val = random.uniform(long_min, long_max)
            return f"{val:.4f}°E"

    def generate(self, sample_size: int) -> pd.DataFrame:
        """Generate a DataFrame of synthetic license data."""
        logger.info(f"Starting generation of {sample_size} records...")
        data = []
        used_bl_numbers = set()
        used_cbls_numbers = set()

        for i in range(sample_size):
            if (i + 1) % 100 == 0:
                logger.info(f"Generated {i + 1}/{sample_size} records...")

            # Core Attributes
            emirate_en = self._choose_weighted(self.emirates)
            emirate_ar = self.emirates_ar[emirate_en]
            authority_choices = self.authorities.get(emirate_en, self.authorities['default'])
            authority = self._choose_weighted(authority_choices)
            authority_ar = self.authorities_ar.get(authority, '')
            license_type = self._choose_weighted(self.license_types)

            # Business Name
            bl_name_en, bl_name_ar = self._generate_business_name(license_type)

            # Unique License Numbers
            while True:
                bl_num = f"BL-{random.randint(100000, 999999)}"
                if bl_num not in used_bl_numbers:
                    used_bl_numbers.add(bl_num)
                    break
            while True:
                cbls_num = f"CBLS-{random.randint(10000, 99999)}"
                if cbls_num not in used_cbls_numbers:
                    used_cbls_numbers.add(cbls_num)
                    break

            # Dates
            est_date = self.fake_en.date_time_between(start_date='-10y', end_date='now').strftime('%d/%m/%Y')
            duration_days = int(np.random.normal(365, 30))
            exp_date = (datetime.strptime(est_date, '%d/%m/%Y') + timedelta(days=duration_days)).strftime('%d/%m/%Y')

            # Categorical data
            status = self._choose_weighted(self.statuses)
            legal_type = self._choose_weighted(self.legal_types)
            nationality = self._choose_weighted(self.nationalities)
            gender = self._choose_weighted(self.genders)
            relationship = self._choose_weighted(self.relationship_types)
            activity_code, activity_en, activity_ar = random.choice(self.activities)

            # Location
            address = self._sanitize(self.fake_en.address())
            lat = self._generate_coordinate(emirate_en, 'lat')
            long = self._generate_coordinate(emirate_en, 'long')

            # Create Record
            record = {
                'Emirate Name En': emirate_en,
                'Emirate Name Ar': emirate_ar,
                'Issuance Authority En': authority,
                'Issuance Authority Ar': authority_ar,
                'Issuance Authority Branch En': 'Main',  # Placeholder
                'Issuance Authority Branch Ar': 'رئيسي',  # Placeholder
                'BL #': bl_num,
                'BL CBLS #': cbls_num,
                'BL Name Ar': bl_name_ar,
                'BL Name En': bl_name_en,
                'BL Est Date': est_date,
                'BL Exp Date': exp_date,
                'BL Status EN': status,
                'BL Status AR': self.statuses_ar.get(status, ''),
                'BL Legal Type En': legal_type,
                'BL Legal Type Ar': self.legal_types_ar.get(legal_type, ''),
                'BL Type En': license_type,
                'BL Type Ar': self.license_types_ar.get(license_type, ''),
                'BL Full Address': address,
                'License Latitude': lat,
                'License Longitude': long,
                'License Branch Flag': 'Y' if random.random() > 0.8 else 'N', # Placeholder
                'Parent Licence - License Number': f"BL-{random.randint(100000, 999999)}" if random.random() > 0.9 else '', # Placeholder
                'Parent License Issuance Authority En': self._choose_weighted(authority_choices) if random.random() > 0.9 else '', # Placeholder
                'Parent License Issuance Authority Ar': self.authorities_ar.get(authority, '') if random.random() > 0.9 else '', # Placeholder
                'Relationship Type En': relationship,
                'Relationship Type Ar': self.relationship_types_ar.get(relationship, ''),
                'Owner Nationality En': nationality,
                'Owner Nationality Ar': self.nationalities_ar.get(nationality, ''),
                'Owner Gender': gender,
                'Business Activity Code': activity_code,
                'Business Activity Desc En': self._sanitize(activity_en),
                'Business Activity Desc Ar': self._sanitize(activity_ar),
            }
            data.append(record)

        df = pd.DataFrame(data)

        # Add a unique primary key
        df['license_pk'] = df.apply(
            lambda row: hashlib.md5(f"{row['Issuance Authority En']}|{row['BL #']}|{row['Business Activity Code']}|{row['Business Activity Desc En']}".encode()).hexdigest(),
            axis=1
        )

        logger.info("Data generation complete.")
        return df


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic UAE business license data.')
    parser.add_argument('--output', type=str, required=True, help='Output file path (CSV)')
    parser.add_argument('--sample-size', type=int, default=1000, help='Number of synthetic records to generate')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--log-level', type=str, default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Set the logging level')

    args = parser.parse_args()

    # Set up logging
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    if args.seed:
        logger.info(f"Using random seed: {args.seed}")
        random.seed(args.seed)
        np.random.seed(args.seed)
        Faker.seed(args.seed)

    generator = SyntheticDataGenerator()
    synthetic_data = generator.generate(args.sample_size)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    synthetic_data.to_csv(output_path, index=False, sep='|', encoding='utf-8')

    logger.info(f"Successfully generated {args.sample_size} records and saved to {args.output}")


if __name__ == '__main__':
    main() 