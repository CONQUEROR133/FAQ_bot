#!/usr/bin/env python3
"""
Configuration Validation Script
Validates environment configuration before deployment
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add src to path - script is in scripts/, so go up one level to project root, then down to src/
# This allows importing the config module from the src directory
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from config import config, SecurityValidator  # type: ignore
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)


class ConfigValidator:
    """Validates bot configuration for deployment."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def validate_bot_token(self) -> bool:
        """Validate bot token format."""
        token = config.BOT_TOKEN
        
        if not token:
            self.errors.append("BOT_TOKEN is not set")
            return False
        
        # Basic bot token format validation
        if not re.match(r'^\d+:[A-Za-z0-9_-]{35}$', token):
            self.errors.append("BOT_TOKEN format appears invalid")
            return False
        
        if token.startswith("your_") or "example" in token.lower():
            self.errors.append("BOT_TOKEN appears to be a placeholder")
            return False
        
        self.info.append("✅ Bot token format is valid")
        return True
    
    def validate_admin_id(self) -> bool:
        """Validate admin ID."""
        admin_id = config.ADMIN_ID
        
        if not admin_id or admin_id <= 0:
            self.errors.append("ADMIN_ID is not set or invalid")
            return False
        
        if admin_id == 123456:  # Common placeholder
            self.warnings.append("ADMIN_ID appears to be a placeholder value")
        
        self.info.append(f"✅ Admin ID is set: {admin_id}")
        return True
    
    def validate_password_strength(self) -> bool:
        """Validate access password strength."""
        password = config.security.access_password
        
        if not password:
            self.errors.append("ACCESS_PASSWORD is not set")
            return False
        
        # Check for common weak passwords
        weak_passwords = ['123', '1337', 'password', 'admin', 'test']
        if password.lower() in weak_passwords:
            self.warnings.append(f"ACCESS_PASSWORD '{password}' is commonly used and weak")
        
        # Use the built-in password strength validator
        if not config.security.validate_password_strength():
            self.warnings.append("ACCESS_PASSWORD does not meet strength requirements")
        else:
            self.info.append("✅ Password meets strength requirements")
        
        return True
    
    def validate_file_paths(self) -> bool:
        """Validate required file paths."""
        paths_to_check = [
            ('FAQ file', config.FAQ_FILE),
            ('Database directory', config.DB_PATH.parent),
            ('Cache directory', config.EMBEDDINGS_FILE.parent),
        ]
        
        all_valid = True
        
        for name, path in paths_to_check:
            if not path.exists():
                if name == "Database directory" or name == "Cache directory":
                    self.warnings.append(f"{name} doesn't exist but will be created: {path}")
                else:
                    self.errors.append(f"{name} not found: {path}")
                    all_valid = False
            else:
                self.info.append(f"✅ {name} exists: {path}")
        
        return all_valid
    
    def validate_security_settings(self) -> bool:
        """Validate security configuration."""
        security = config.security
        
        # Check rate limiting
        if not security.enable_rate_limiting:
            self.warnings.append("Rate limiting is disabled - consider enabling for production")
        
        # Check request limits
        if security.max_requests_per_minute > 100:
            self.warnings.append(f"High rate limit: {security.max_requests_per_minute}/min")
        
        # Check blocked words
        if not security.blocked_words:
            self.warnings.append("No blocked words configured")
        elif len(security.blocked_words) < 3:
            self.warnings.append("Very few blocked words configured")
        
        self.info.append("✅ Security settings validated")
        return True
    
    def validate_ml_settings(self) -> bool:
        """Validate ML configuration."""
        ml = config.ml
        
        # Check similarity threshold
        if ml.similarity_threshold < 0.5:
            self.warnings.append(f"Low similarity threshold: {ml.similarity_threshold}")
        elif ml.similarity_threshold > 0.9:
            self.warnings.append(f"High similarity threshold: {ml.similarity_threshold}")
        
        # Check model name
        if "test" in ml.model_name.lower() or "example" in ml.model_name.lower():
            self.warnings.append("ML model name appears to be a placeholder")
        
        self.info.append(f"✅ ML model: {ml.model_name}")
        self.info.append(f"✅ Similarity threshold: {ml.similarity_threshold}")
        return True
    
    def validate_network_settings(self) -> bool:
        """Validate network configuration."""
        network = config.network
        
        # Check timeouts
        if network.request_timeout < 10:
            self.warnings.append(f"Short request timeout: {network.request_timeout}s")
        elif network.request_timeout > 60:
            self.warnings.append(f"Long request timeout: {network.request_timeout}s")
        
        # Check retries
        if network.max_retries > 10:
            self.warnings.append(f"High retry count: {network.max_retries}")
        
        self.info.append("✅ Network settings validated")
        return True
    
    def validate_environment(self) -> bool:
        """Validate environment-specific settings."""
        debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        if debug_mode:
            self.warnings.append("Debug mode is enabled - disable for production")
        
        if log_level == 'DEBUG':
            self.warnings.append("Debug logging enabled - consider INFO for production")
        
        self.info.append(f"✅ Debug mode: {debug_mode}")
        self.info.append(f"✅ Log level: {log_level}")
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        required_modules = [
            'aiogram',
            'sentence_transformers', 
            'faiss',
            'numpy',
            'pandas'
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            self.errors.append(f"Missing dependencies: {', '.join(missing)}")
            return False
        
        self.info.append("✅ All required dependencies are available")
        return True
    
    def validate_all(self) -> bool:
        """Run all validations."""
        validations = [
            self.validate_bot_token,
            self.validate_admin_id,
            self.validate_password_strength,
            self.validate_file_paths,
            self.validate_security_settings,
            self.validate_ml_settings,
            self.validate_network_settings,
            self.validate_environment,
            self.check_dependencies
        ]
        
        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"Validation error: {e}")
                all_passed = False
        
        return all_passed
    
    def print_results(self):
        """Print validation results."""
        print("🔍 Configuration Validation Results")
        print("=" * 50)
        
        # Print errors
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        # Print warnings
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Print info
        if self.info:
            print("\n✅ INFORMATION:")
            for info in self.info:
                print(f"  • {info}")
        
        # Summary
        print("\n" + "=" * 50)
        if self.errors:
            print("❌ VALIDATION FAILED - Fix errors before deployment")
            return False
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS - Review before production")
            return True
        else:
            print("✅ VALIDATION PASSED - Configuration is ready for deployment")
            return True


def main():
    """Main validation function."""
    print("🚀 FAQ Bot Configuration Validator")
    print("Checking configuration for deployment readiness...\n")
    
    validator = ConfigValidator()
    success = validator.validate_all()
    validator.print_results()
    
    # Exit with appropriate code
    if not success:
        sys.exit(1)
    elif validator.warnings:
        sys.exit(2)  # Warnings present
    else:
        sys.exit(0)  # All good


if __name__ == "__main__":
    main()