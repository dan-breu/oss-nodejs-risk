import json
import csv
import sys
import re
from typing import Dict, List, Any, Optional

def extract_cvss_score(severity_list: List[Dict]) -> float:
    """Extract CVSS score from severity information."""
    for severity in severity_list:
        if severity.get("type") == "CVSS_V3":
            score_string = severity.get("score", "")
            # Extract numeric score from CVSS string like "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H"
            # Look for the base score which is typically calculated from the vector
            # For now, we'll try to extract from the max_severity in groups
            pass
    return 0.0

def extract_max_severity_score(groups: List[Dict]) -> float:
    """Extract maximum severity score from groups."""
    max_score = 0.0
    for group in groups:
        score_str = group.get("max_severity", "0")
        try:
            score = float(score_str)
            max_score = max(max_score, score)
        except (ValueError, TypeError):
            continue
    return max_score

def extract_severity_level(severity_list: List[Dict], database_specific: Dict) -> str:
    """Extract severity level (HIGH, MEDIUM, LOW, etc.)."""
    # First check database_specific for severity
    db_severity = database_specific.get("severity", "")
    if db_severity:
        return db_severity.upper()
    
    # If not found, try to determine from CVSS score
    for severity in severity_list:
        if severity.get("type") == "CVSS_V3":
            score_string = severity.get("score", "")
            # We'll use the max_severity from groups instead
            break
    
    return "UNKNOWN"

def extract_cve_id(aliases: List[str]) -> str:
    """Extract CVE ID from aliases list."""
    for alias in aliases:
        if alias.startswith("CVE-"):
            return alias
    return "NA"

def extract_fixed_version(affected_packages: List[Dict], package_name: str) -> str:
    """Extract fixed version from affected packages."""
    for package_info in affected_packages:
        package = package_info.get("package", {})
        if package.get("name") == package_name:
            ranges = package_info.get("ranges", [])
            for range_info in ranges:
                events = range_info.get("events", [])
                for event in events:
                    if "fixed" in event:
                        return event["fixed"]
    return "NA"

def process_osv_report(json_file_path: str, csv_file_path: str) -> None:
    """Convert OSV scan report JSON to CSV format."""
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Open CSV file for writing
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write header
            csv_writer.writerow([
                "name", "version", "fixed", "cvss", "cve", "severity"
            ])
            
            # Process results
            results = data.get("results", [])
            
            for result in results:
                packages = result.get("packages", [])
                
                for package_data in packages:
                    package = package_data.get("package", {})
                    package_name = package.get("name", "")
                    package_version = package.get("version", "")
                    
                    vulnerabilities = package_data.get("vulnerabilities", [])
                    groups = package_data.get("groups", [])
                    
                    # Get max severity score from groups
                    max_cvss = extract_max_severity_score(groups)
                    
                    for vulnerability in vulnerabilities:
                        # Extract CVE from aliases
                        aliases = vulnerability.get("aliases", [])
                        cve_id = extract_cve_id(aliases)
                        
                        # Extract severity information
                        severity_list = vulnerability.get("severity", [])
                        database_specific = vulnerability.get("database_specific", {})
                        severity_level = extract_severity_level(severity_list, database_specific)
                        
                        # Extract fixed version
                        affected_packages = vulnerability.get("affected", [])
                        fixed_version = extract_fixed_version(affected_packages, package_name)
                        
                        # Use max_severity from groups if available, otherwise try to extract from CVSS
                        cvss_score = max_cvss if max_cvss > 0 else 0.0
                        
                        # If we still don't have a CVSS score, try to extract from the CVSS string
                        if cvss_score == 0.0:
                            for severity in severity_list:
                                if severity.get("type") == "CVSS_V3":
                                    score_string = severity.get("score", "")
                                    # Try to extract base score from CVSS vector
                                    # This is a simplified approach - in reality, you'd calculate from the vector
                                    if "AV:N" in score_string:  # Network accessible
                                        if "AC:L" in score_string and "PR:N" in score_string:  # Low complexity, no privileges
                                            if "I:H" in score_string or "A:H" in score_string:  # High impact
                                                cvss_score = 7.5  # Rough estimate
                                            else:
                                                cvss_score = 5.0
                                    break
                        
                        # Write row to CSV
                        csv_writer.writerow([
                            package_name,
                            package_version,
                            fixed_version,
                            cvss_score if cvss_score > 0 else "NA",
                            cve_id,
                            severity_level
                        ])
        
        print(f"Successfully converted {json_file_path} to {csv_file_path}")
        
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 3:
        print("Usage: python osv_to_csv.py <input_osv_json_file> <output_csv_file>")
        print("Example: python osv_to_csv.py mongoose.osv.json vulnerabilities.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_osv_report(input_file, output_file)

if __name__ == "__main__":
    main()