import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import json
from dataclasses import dataclass, asdict, field
import hashlib

USASPENDING_API = "https://api.usaspending.gov/api/v2"


@dataclass
class Address:
    """Address data model for entity location"""
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"
    
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v}

@dataclass
class ActivitySignal:
    """Activity signal representing a contract award event"""
    signal_type: str
    timestamp: str
    amount: Optional[float] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ContractMetrics:
    """Aggregated contract metrics for an entity"""
    total_contract_value: float
    contract_count: int
    avg_contract_size: float
    most_recent_award_date: str
    oldest_award_date: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class EnigmaBrandEntity:
    """Brand entity mapped to Enigma ontology"""
    entity_id: str
    entity_type: str = "Brand"
    
    primary_name: str = None
    alternate_names: List[str] = field(default_factory=list)
    operating_location: Optional[Address] = None
    activity_signals: List[ActivitySignal] = field(default_factory=list)
    contract_metrics: Optional[ContractMetrics] = None
    data_sources: List[str] = field(default_factory=lambda: ["USAspending"])
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        result = {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "primary_name": self.primary_name,
            "alternate_names": self.alternate_names,
            "data_sources": self.data_sources,
            "last_updated": self.last_updated
        }
        
        if self.operating_location:
            result["operating_location"] = self.operating_location.to_dict()
        
        if self.activity_signals:
            result["activity_signals"] = [s.to_dict() for s in self.activity_signals]
        
        if self.contract_metrics:
            result["contract_metrics"] = self.contract_metrics.to_dict()
        
        return {k: v for k, v in result.items() if v}


class USAspendingExtractor:
    """Extracts subaward data from USAspending API"""
    def __init__(self):
        self.base_url = USASPENDING_API
        self.session = requests.Session()
    
    def search_subawards(
        self,
        start_date: str = "2023-01-01",
        end_date: str = "2024-12-31",
        limit: int = 100
    ) -> List[Dict]:
        url = f"{self.base_url}/subawards/"
        
        payload = {
            "filters": {
                "time_period": [
                    {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                ],
                "award_type_codes": ["B", "C", "D"],  # B=Contract, C=IDV, D=Definitive Contract
            },
            "fields": [
                "subaward_number",
                "recipient_name",
                "amount",
                "action_date",
                "description"
            ],
            "limit": limit,
            "page": 1
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                return results
            else:
                error_msg = f"API returned status {response.status_code}"
                if response.status_code == 401:
                    error_msg += " - Authentication failed. Check your API key."
                elif response.status_code == 429:
                    error_msg += " - Rate limit exceeded."
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call failed: {e}")
        except Exception as e:
            raise


class DataTransformer:
    """Cleans and transforms raw API data"""
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        
        # Map API column names to standardized format
        column_mapping = {
            'recipient_name': 'Recipient Name',
            'award_amount': 'Award Amount',
            'amount': 'Award Amount',
            'start_date': 'Start Date',
            'action_date': 'Start Date',
            'award_id': 'Award ID',
            'id': 'Award ID',
            'subaward_number': 'Award ID',
            'award_type': 'Award Type',
            'recipient_city': 'Recipient City',
            'recipient_state': 'Recipient State',
            'recipient_zip': 'Recipient ZIP',
        }
        
        if 'subaward_number' in df_clean.columns and 'Award ID' not in df_clean.columns:
            df_clean.rename(columns={'subaward_number': 'Award ID'}, inplace=True)
        elif 'id' in df_clean.columns and 'Award ID' not in df_clean.columns:
            df_clean.rename(columns={'id': 'Award ID'}, inplace=True)
        
        for old_name, new_name in column_mapping.items():
            if old_name in df_clean.columns and new_name not in df_clean.columns:
                df_clean.rename(columns={old_name: new_name}, inplace=True)
        
        recipient_col = None
        if 'Recipient Name' in df_clean.columns:
            recipient_col = 'Recipient Name'
        elif 'recipient_name' in df_clean.columns:
            df_clean.rename(columns={'recipient_name': 'Recipient Name'}, inplace=True)
            recipient_col = 'Recipient Name'
        
        if recipient_col:
            # Normalize recipient names for grouping
            df_clean['Recipient Name Clean'] = (
                df_clean['Recipient Name']
                .str.upper()
                .str.strip()
            )
        else:
            df_clean['Recipient Name Clean'] = ''
        
        if 'Start Date' in df_clean.columns:
            df_clean['Start Date'] = pd.to_datetime(df_clean['Start Date'], errors='coerce')
        elif 'action_date' in df_clean.columns:
            df_clean['action_date'] = pd.to_datetime(df_clean['action_date'], errors='coerce')
            df_clean['Start Date'] = df_clean['action_date']
        
        if 'Award Amount' in df_clean.columns:
            df_clean['Award Amount'] = pd.to_numeric(df_clean['Award Amount'], errors='coerce')
        elif 'amount' in df_clean.columns:
            df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')
            df_clean['Award Amount'] = df_clean['amount']
        
        return df_clean
    
    def aggregate_by_recipient(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates contracts by recipient entity"""
        agg_dict = {}
        
        if 'Recipient Name' in df.columns:
            agg_dict['Recipient Name'] = 'first'
        
        if 'Award Amount' in df.columns:
            agg_dict['Award Amount'] = ['sum', 'count', 'mean']
        elif 'amount' in df.columns:
            agg_dict['amount'] = ['sum', 'count', 'mean']
        
        if 'Start Date' in df.columns:
            agg_dict['Start Date'] = ['min', 'max']
        elif 'action_date' in df.columns:
            agg_dict['action_date'] = ['min', 'max']
        
        if 'Award Type' in df.columns:
            agg_dict['Award Type'] = lambda x: list(x.unique())
        if 'Award ID' in df.columns:
            agg_dict['Award ID'] = 'count'
        if 'Recipient City' in df.columns:
            agg_dict['Recipient City'] = 'first'
        if 'Recipient State' in df.columns:
            agg_dict['Recipient State'] = 'first'
        if 'Recipient ZIP' in df.columns:
            agg_dict['Recipient ZIP'] = 'first'
        
        if not agg_dict:
            raise ValueError("No valid columns found for aggregation")
        
        grouped = df.groupby('Recipient Name Clean').agg(agg_dict).reset_index()
        
        # Flatten MultiIndex columns from pandas aggregation
        column_names = []
        
        for col in grouped.columns:
            if isinstance(col, tuple):
                col_name, agg_func = col
                
                if col_name == 'Recipient Name Clean':
                    column_names.append('recipient_name_clean')
                elif col_name == 'Recipient Name' and agg_func == 'first':
                    column_names.append('recipient_name')
                elif col_name in ['Award Amount', 'amount']:
                    if agg_func == 'sum':
                        column_names.append('total_award_amount')
                    elif agg_func == 'count':
                        column_names.append('contract_count')
                    elif agg_func == 'mean':
                        column_names.append('avg_award_amount')
                    else:
                        column_names.append(f"{col_name.lower().replace(' ', '_')}_{agg_func}")
                elif col_name in ['Start Date', 'action_date']:
                    if agg_func == 'min':
                        column_names.append('earliest_award')
                    elif agg_func == 'max':
                        column_names.append('latest_award')
                    else:
                        column_names.append(f"{col_name.lower().replace(' ', '_')}_{agg_func}")
                elif col_name == 'Award ID' and agg_func == 'count':
                    column_names.append('award_id_count')
                else:
                    base_name = col_name.lower().replace(' ', '_')
                    if agg_func and agg_func != '':
                        column_names.append(f"{base_name}_{agg_func}")
                    else:
                        column_names.append(base_name)
            else:
                col_str = str(col).lower().replace(' ', '_')
                if col == 'Recipient Name Clean':
                    column_names.append('recipient_name_clean')
                elif col == 'Recipient Name':
                    column_names.append('recipient_name')
                elif col == 'Award Type':
                    column_names.append('award_types')
                elif col == 'Award ID':
                    column_names.append('award_id_count')
                elif col == 'Recipient City':
                    column_names.append('city')
                elif col == 'Recipient State':
                    column_names.append('state')
                elif col == 'Recipient ZIP':
                    column_names.append('zip_code')
                else:
                    column_names.append(col_str)
        
        if len(column_names) != len(grouped.columns):
            # Fallback: auto-generate column names if mismatch occurs
            if isinstance(grouped.columns, pd.MultiIndex):
                column_names = []
                for col in grouped.columns:
                    if isinstance(col, tuple):
                        col_name, agg_func = col
                        if agg_func and agg_func != '':
                            column_names.append(f"{str(col_name).lower().replace(' ', '_')}_{agg_func}")
                        else:
                            column_names.append(str(col_name).lower().replace(' ', '_'))
                    else:
                        column_names.append(str(col).lower().replace(' ', '_'))
            else:
                column_names = [str(col).lower().replace(' ', '_') for col in grouped.columns]
        
        grouped.columns = column_names
        return grouped


class EnigmaMapper:
    """Maps transformed data to Enigma entity format"""
    def generate_entity_id(self, name: str, location: str = "") -> str:
        """Generates deterministic entity ID from name and location"""
        key = f"{name}|{location}"
        return "B" + hashlib.md5(key.encode()).hexdigest()[:15]
    
    def create_address(self, row: pd.Series) -> Optional[Address]:
        if pd.isna(row.get('city')) and pd.isna(row.get('state')):
            return None
        
        return Address(
            city=row.get('city'),
            state=row.get('state'),
            zip_code=row.get('zip_code')
        )
    
    def create_activity_signals(self, recipient_name: str, df_contracts: pd.DataFrame) -> List[ActivitySignal]:
        signals = []
        contracts = df_contracts[df_contracts['Recipient Name Clean'] == recipient_name]
        
        for _, contract in contracts.iterrows():
            signal = ActivitySignal(
                signal_type="federal_contract_awarded",
                timestamp=contract.get('Start Date').isoformat() if pd.notna(contract.get('Start Date')) else datetime.now().isoformat(),
                amount=float(contract.get('Award Amount', 0)) if pd.notna(contract.get('Award Amount')) else None,
                metadata={
                    "award_id": contract.get('Award ID', ''),
                    "contract_type": contract.get('Award Type', 'Contract'),
                    "description": contract.get('description', '')
                }
            )
            signals.append(signal)
        
        return signals
    
    def calculate_contract_metrics(self, row: pd.Series) -> ContractMetrics:
        return ContractMetrics(
            total_contract_value=float(row.get('total_award_amount', 0)),
            contract_count=int(row.get('contract_count', 0)),
            avg_contract_size=float(row.get('avg_award_amount', 0)),
            most_recent_award_date=row.get('latest_award').isoformat() if pd.notna(row.get('latest_award')) else '',
            oldest_award_date=row.get('earliest_award').isoformat() if pd.notna(row.get('earliest_award')) else ''
        )
    
    def map_to_entity(self, row: pd.Series, df_contracts: pd.DataFrame) -> EnigmaBrandEntity:
        location_key = f"{row.get('city', '')}{row.get('state', '')}"
        entity_id = self.generate_entity_id(row.get('recipient_name_clean', ''), location_key)
        address = self.create_address(row)
        activity_signals = self.create_activity_signals(row.get('recipient_name_clean', ''), df_contracts)
        metrics = self.calculate_contract_metrics(row)
        
        entity = EnigmaBrandEntity(
            entity_id=entity_id,
            primary_name=row.get('recipient_name', 'Unknown'),
            operating_location=address,
            activity_signals=activity_signals,
            contract_metrics=metrics
        )
        
        return entity


class Validator:
    """Validates entity data quality"""
    def validate_entities(self, entities: List[EnigmaBrandEntity]) -> Dict:
        if not entities:
            return {
                "total_entities": 0,
                "with_location": 0,
                "with_contracts": 0,
                "avg_contracts_per_entity": 0.0,
                "total_contract_value": 0.0
            }
        
        results = {
            "total_entities": len(entities),
            "with_location": sum(1 for e in entities if e.operating_location),
            "with_contracts": sum(1 for e in entities if e.activity_signals),
            "avg_contracts_per_entity": np.mean([len(e.activity_signals) for e in entities]) if entities else 0.0,
            "total_contract_value": sum(e.contract_metrics.total_contract_value for e in entities if e.contract_metrics)
        }
        
        return results
    
    def print_validation_report(self, validation: Dict):
        """Prints standard validation output"""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        print(f"Total entities: {validation['total_entities']}")
        
        if validation['total_entities'] > 0:
            print(f"With location data: {validation['with_location']} ({validation['with_location']/validation['total_entities']*100:.1f}%)")
            print(f"With contracts: {validation['with_contracts']} ({validation['with_contracts']/validation['total_entities']*100:.1f}%)")
            print(f"Avg contracts per entity: {validation['avg_contracts_per_entity']:.1f}")
        else:
            print("Warning: No entities found")
        
        print(f"Total contract value: ${validation['total_contract_value']:,.0f}")
        print("="*60 + "\n")


def export_entities(entities: List[EnigmaBrandEntity], filename: str = "enigma_entities.json"):
    output = {
        "metadata": {
            "source": "USAspending API",
            "extraction_date": datetime.now().isoformat(),
            "entity_count": len(entities),
            "parser_version": "1.0"
        },
        "entities": [e.to_dict() for e in entities]
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    return filename


if __name__ == "__main__":
    extractor = USAspendingExtractor()
    raw_data = extractor.search_subawards(limit=100)
    df_raw = pd.DataFrame(raw_data)
    
    transformer = DataTransformer()
    df_clean = transformer.clean_data(df_raw)
    df_aggregated = transformer.aggregate_by_recipient(df_clean)
    
    mapper = EnigmaMapper()
    entities = []
    for idx, row in df_aggregated.iterrows():
        entity = mapper.map_to_entity(row, df_clean)
        entities.append(entity)
    
    # Validate and report
    validator = Validator()
    validation = validator.validate_entities(entities)
    validator.print_validation_report(validation)
    
    # Export
    output_file = export_entities(entities)
    print(f"Exported {len(entities)} entities to {output_file}")