#!/usr/bin/env python3
"""
Test environment for parser development
Tests parser without database dependencies
"""

import re
import sys
import os
from typing import List, Dict, Any, Optional

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class TestMariaDBParser:
    """Test version of parser that doesn't require database connection"""
    
    def __init__(self, sql_file_path: str):
        self.sql_file_path = sql_file_path
        self.records = []
        self.kidnapping_records = []
        
    def parse_sql_export(self) -> List[Dict[str, Any]]:
        """Parse MariaDB SQL export file and extract conflict records"""
        print(f"🔍 Parsing SQL file: {self.sql_file_path}")
        
        try:
            with open(self.sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Failed to read SQL file: {e}")
            return []
        
        # NEW APPROACH: Find ALL INSERT statements, not just first one
        all_inserts = re.findall(
            r'INSERT INTO `conflicts`.*?VALUES\s*(.+?);', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        print(f"📊 Found {len(all_inserts)} INSERT statements")
        
        all_records = []
        for i, values_str in enumerate(all_inserts):
            print(f"🔄 Processing INSERT {i+1}/{len(all_inserts)}...")
            
            # Parse individual records from this INSERT statement
            records = self._parse_insert_values(values_str, i+1)
            all_records.extend(records)
            
            print(f"   ✅ Parsed {len(records)} records from INSERT {i+1}")
        
        print(f"🎉 Total records parsed: {len(all_records)}")
        self.records = all_records
        return all_records
    
    def _parse_insert_values(self, values_str: str, insert_num: int) -> List[Dict[str, Any]]:
        """Parse individual records from INSERT VALUES clause"""
        records = []
        current_record = ''
        paren_count = 0
        in_quotes = False
        quote_char = None
        record_count = 0
        
        for i, char in enumerate(values_str):
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == '(' and not in_quotes:
                paren_count += 1
                current_record += char
            elif char == ')' and not in_quotes:
                paren_count -= 1
                current_record += char
                if paren_count == 0:
                    record_count += 1
                    try:
                        parsed_record = self._parse_single_record(current_record.strip(), record_count, insert_num)
                        if parsed_record:
                            records.append(parsed_record)
                    except Exception as e:
                        print(f"   ⚠️  Failed to parse record {record_count} in INSERT {insert_num}: {e}")
                    current_record = ''
            else:
                current_record += char
        
        print(f"   📈 INSERT {insert_num}: {len(records)} valid records from {record_count} total")
        return records
    
    def _parse_single_record(self, record_str: str, record_id: int, insert_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single record string into structured data"""
        # Remove outer parentheses
        if record_str.startswith('(') and record_str.endswith(')'):
            record_str = record_str[1:-1]
        
        # Parse values handling quoted strings and NULL values
        values = []
        current_val = ''
        in_val_quotes = False
        val_quote_char = None
        
        for char in record_str:
            if char in ("'", '"') and not in_val_quotes:
                in_val_quotes = True
                val_quote_char = char
            elif char == val_quote_char and in_val_quotes:
                in_val_quotes = False
                val_quote_char = None
            elif char == ',' and not in_val_quotes:
                values.append(current_val.strip())
                current_val = ''
            else:
                current_val += char
        
        if current_val.strip():
            values.append(current_val.strip())
        
        # Validate we have enough columns
        if len(values) < 24:
            return None
        
        try:
            # Extract key fields with proper type conversion
            parsed_data = {
                'record_id': record_id,
                'insert_num': insert_num,
                'id': self._safe_int(values[0]),
                'incidence_date': self._parse_date(values[1]),
                'conflict_type_id': self._safe_int(values[2]),
                'state_id': self._safe_int(values[5]),
                'lga_id': self._safe_int(values[6]),
                'community': self._clean_string(values[7]),
                
                # Death data
                'civilian_death_male': self._safe_int(values[9]),
                'civilian_death_female': self._safe_int(values[10]),
                'civilian_death_unknown': self._safe_int(values[11]),
                'security_death_male': self._safe_int(values[12]),
                'security_death_female': self._safe_int(values[13]),
                'security_death_unknown': self._safe_int(values[14]),
                
                # Injury data
                'injured_male': self._safe_int(values[15]),
                'injured_female': self._safe_int(values[16]),
                'injured_unknown': self._safe_int(values[17]),
                
                # Kidnapping data (key focus)
                'kidnapped_male': self._safe_int(values[18]),
                'kidnapped_female': self._safe_int(values[19]),
                'kidnapped_unknown': self._safe_int(values[20]),
                
                # Other fields
                'displaced_persons': self._clean_string(values[21]),
                'actor_1': self._safe_int(values[22]),
                'description': self._clean_string(values[23]),
                'source_url': self._clean_string(values[27]) if len(values) > 27 else '',
                'data_source': self._clean_string(values[30]) if len(values) > 30 else '',
            }
            
            # Calculate totals
            parsed_data['total_deaths'] = (
                parsed_data['civilian_death_male'] + parsed_data['civilian_death_female'] + 
                parsed_data['civilian_death_unknown'] + parsed_data['security_death_male'] + 
                parsed_data['security_death_female'] + parsed_data['security_death_unknown']
            )
            parsed_data['total_injured'] = (
                parsed_data['injured_male'] + parsed_data['injured_female'] + parsed_data['injured_unknown']
            )
            parsed_data['total_kidnapped'] = (
                parsed_data['kidnapped_male'] + parsed_data['kidnapped_female'] + parsed_data['kidnapped_unknown']
            )
            
            return parsed_data
            
        except Exception as e:
            print(f"   ❌ Error parsing record {record_id} in INSERT {insert_num}: {e}")
            return None
    
    def _safe_int(self, value: str) -> int:
        """Safely convert string to int, handling NULL and other values"""
        value = value.strip().strip("'")
        if value == 'NULL' or value == '' or not value.isdigit():
            return 0
        return int(value)
    
    def _parse_date(self, value: str) -> Optional[str]:
        """Parse date string and return ISO format"""
        value = value.strip().strip("'")
        if value == 'NULL' or value == '' or value == '0':
            return None
        
        try:
            # Handle various date formats
            if re.match(r'\d{4}-\d{2}-\d{2}', value):
                return value  # Already in YYYY-MM-DD format
            else:
                # Try to parse other formats
                from datetime import datetime
                dt = datetime.strptime(value, '%Y-%m-%d')
                return dt.strftime('%Y-%m-%d')
        except Exception:
            return None
    
    def _clean_string(self, value: str) -> str:
        """Clean string value by removing quotes and trimming"""
        value = value.strip().strip("'").strip()
        # Handle special cases
        if value == 'NULL' or value == '0' or value == '':
            return ''
        return value
    
    def extract_kidnapping_records(self) -> List[Dict[str, Any]]:
        """Extract records with kidnapping data"""
        if not self.records:
            print("⚠️  No records parsed yet")
            return []
        
        kidnapping_records = []
        for record in self.records:
            if record['total_kidnapped'] > 0:
                kidnapping_records.append(record)
        
        print(f"🎯 Found {len(kidnapping_records)} records with kidnapping data")
        self.kidnapping_records = kidnapping_records
        return kidnapping_records
    
    def validate_parsed_data(self) -> Dict[str, Any]:
        """Validate parsed data and return statistics"""
        if not self.records:
            return {'error': 'No data parsed'}
        
        stats = {
            'total_records': len(self.records),
            'kidnapping_records': len(self.kidnapping_records),
            'total_kidnapped': sum(r['total_kidnapped'] for r in self.kidnapping_records),
            'total_deaths': sum(r['total_deaths'] for r in self.records),
            'records_with_dates': len([r for r in self.records if r['incidence_date']]),
            'unique_states': len(set(r['state_id'] for r in self.records if r['state_id'] > 0)),
        }
        
        # Validate kidnapping data specifically
        if self.kidnapping_records:
            stats['kidnapping_by_gender'] = {
                'male': sum(r['kidnapped_male'] for r in self.kidnapping_records),
                'female': sum(r['kidnapped_female'] for r in self.kidnapping_records),
                'unknown': sum(r['kidnapped_unknown'] for r in self.kidnapping_records),
            }
        
        return stats

def test_new_parser():
    """Test the new multi-INSERT parser"""
    sql_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
    
    print("=== TESTING NEW MULTI-INSERT PARSER ===")
    
    parser = TestMariaDBParser(sql_file)
    
    # Parse the SQL export
    records = parser.parse_sql_export()
    
    # Extract kidnapping records
    kidnapping_records = parser.extract_kidnapping_records()
    
    # Validate data
    validation = parser.validate_parsed_data()
    
    print(f"\n=== PARSING RESULTS ===")
    print(f"📊 Total records: {validation.get('total_records', 0)}")
    print(f"🎯 Kidnapping records: {validation.get('kidnapping_records', 0)}")
    print(f"👥 Total kidnapping victims: {validation.get('total_kidnapped', 0)}")
    
    if validation.get('kidnapping_by_gender'):
        gender = validation['kidnapping_by_gender']
        print(f"👨 Male victims: {gender['male']}")
        print(f"👩 Female victims: {gender['female']}")
        print(f"❓ Unknown victims: {gender['unknown']}")
    
    print(f"📅 Records with dates: {validation.get('records_with_dates', 0)}")
    print(f"🗺️  Unique states: {validation.get('unique_states', 0)}")
    
    # Show sample records
    if kidnapping_records:
        print(f"\n=== SAMPLE KIDNAPPING RECORDS ===")
        for i, record in enumerate(kidnapping_records[:3], 1):
            print(f"{i}. ID: {record['id']}, Date: {record['incidence_date']}, Victims: {record['total_kidnapped']}")
            print(f"   Community: {record['community']}, Actor: {record['actor_1']}")
            print(f"   Gender breakdown: M:{record['kidnapped_male']}, F:{record['kidnapped_female']}, U:{record['kidnapped_unknown']}")
            print(f"   From INSERT statement: {record['insert_num']}")
            print()
    
    return validation

if __name__ == "__main__":
    test_new_parser()
