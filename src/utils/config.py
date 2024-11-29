import os
import json
from typing import Dict, Any
from utils.logger import log

def load_industry_configs() -> Dict[str, Any]:
    """Load industry configurations from JSON file."""
    config_path = os.getenv('INDUSTRY_CONFIG_PATH', 'src/config/industries.json')
    
    try:
        with open(config_path, 'r') as f:
            configs = json.load(f)
            
        # Validate configurations
        for industry_id, config in configs.items():
            if not _validate_industry_config(industry_id, config):
                log.error(f"Invalid configuration for industry {industry_id}")
                del configs[industry_id]
                
        return configs
    except Exception as e:
        log.error(f"Error loading industry configurations: {str(e)}")
        return {}

def _validate_industry_config(industry_id: str, config: Dict[str, Any]) -> bool:
    """Validate industry configuration."""
    required_fields = {'protocol', 'server_link' if config.get('protocol') == 'ApodiOpcua' else 'broker'}
    
    return all(field in config for field in required_fields)