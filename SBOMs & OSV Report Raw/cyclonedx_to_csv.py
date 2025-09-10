import json
import csv
import sys
from typing import Dict, List, Any, Optional

def extract_license(licenses: List[Dict]) -> str:
    """Extract license information from the licenses array."""
    if not licenses:
        return "NA"
    
    # Get the first license
    license_info = licenses[0].get("license", {})
    
    # Check for license ID first, then name
    if "id" in license_info:
        return license_info["id"]
    elif "name" in license_info:
        return license_info["name"]
    else:
        return "NA"

def get_component_info(component: Dict[str, Any]) -> Dict[str, str]:
    """Extract relevant information from a component."""
    return {
        "name": component.get("name", "NA"),
        "version": component.get("version", "NA"),
        "type": component.get("type", "NA"),
        "author": component.get("author", "NA"),
        "license": extract_license(component.get("licenses", []))
    }

def process_components(root_info: Dict[str, str], components: List[Dict], csv_writer) -> None:
    """Process components and write to CSV."""
    for component in components:
        child_info = get_component_info(component)
        
        # Write the main component
        csv_writer.writerow([
            root_info["name"],
            root_info["version"],
            root_info["author"],
            root_info["license"],
            child_info["name"],
            child_info["version"],
            child_info["type"],
            child_info["author"],
            child_info["license"]
        ])
        
        # Process nested components if they exist
        if "components" in component:
            process_components(root_info, component["components"], csv_writer)

def process_dependencies(root_info: Dict[str, str], dependencies: List[Dict], 
                        components_map: Dict[str, Dict], csv_writer) -> None:
    """Process dependencies and write to CSV."""
    for dependency in dependencies:
        ref = dependency.get("ref")
        if ref and ref in components_map:
            child_info = components_map[ref]
            
            csv_writer.writerow([
                root_info["name"],
                root_info["version"],
                root_info["author"],
                root_info["license"],
                child_info["name"],
                child_info["version"],
                child_info["type"],
                child_info["author"],
                child_info["license"]
            ])

def build_components_map(components: List[Dict]) -> Dict[str, Dict]:
    """Build a mapping of bom-ref to component info for dependency resolution."""
    components_map = {}
    
    def add_to_map(comp_list: List[Dict]):
        for component in comp_list:
            bom_ref = component.get("bom-ref")
            if bom_ref:
                components_map[bom_ref] = get_component_info(component)
            
            # Process nested components
            if "components" in component:
                add_to_map(component["components"])
    
    add_to_map(components)
    return components_map

def convert_cyclonedx_to_csv(json_file_path: str, csv_file_path: str) -> None:
    """Convert CycloneDX JSON file to CSV format."""
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extract root component information
        root_component = data.get("metadata", {}).get("component", {})
        root_info = get_component_info(root_component)
        
        # Open CSV file for writing
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write header
            csv_writer.writerow([
                "Project Name", "Project Version", "Project Author", "Project License",
                "Library Name", "Library Version", "Library Type", "Library Author", "Library License"
            ])
            
            # Process components directly listed in the components array
            components = data.get("components", [])
            if components:
                process_components(root_info, components, csv_writer)
            
            # Process dependencies if they exist
            dependencies = data.get("dependencies", [])
            if dependencies:
                # Build a map of all components for dependency resolution
                components_map = build_components_map(components)
                
                # Add root component to the map
                root_bom_ref = root_component.get("bom-ref")
                if root_bom_ref:
                    components_map[root_bom_ref] = root_info
                
                # Process dependencies
                for dependency in dependencies:
                    ref = dependency.get("ref")
                    depends_on = dependency.get("dependsOn", [])
                    
                    # If this is the root component, process its dependencies
                    if ref == root_bom_ref or ref == f"{root_info['name']}@{root_info['version']}":
                        for dep_ref in depends_on:
                            if dep_ref in components_map:
                                child_info = components_map[dep_ref]
                                csv_writer.writerow([
                                    root_info["name"],
                                    root_info["version"],
                                    root_info["author"],
                                    root_info["license"],
                                    child_info["name"],
                                    child_info["version"],
                                    child_info["type"],
                                    child_info["author"],
                                    child_info["license"]
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
        print("Usage: python cyclonedx_to_csv.py <input_json_file> <output_csv_file>")
        print("Example: python cyclonedx_to_csv.py mongoose-cdx.json output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    convert_cyclonedx_to_csv(input_file, output_file)

if __name__ == "__main__":
    main()