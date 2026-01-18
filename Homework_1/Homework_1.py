import json
import subprocess
import yaml

BILLING_ACCOUNT_ID = "01689F-2FC313-8F3470" # Billing Account ID for GCP Project.
CATALOG_FILE_PATH = "/Users/rstoffel/PycharmProjects/CSC323/Homework_1/JSON/catalog.json" # File path for catalog.json.
ARCHITECTURE_FILE_PATH = "/Users/rstoffel/PycharmProjects/CSC323/Homework_1/JSON/architecture.json" # File path for architecture.json.

# Function to load JSON files.
def load_json_files(file_name):
    with open(file_name, "r") as file:
        return json.load(file)

# Function to calculate itemized costs.
def calculate_itemized_cost(catalog_file, architecture_file):
    catalog = load_json_files(catalog_file)
    architecture = load_json_files(architecture_file)

    catalog_types_cost = {} # Define a dictionary to store catalog types and their corresponding costs.
    itemized_costs = ""

    for key, value in catalog.items():
        catalog_types_cost[key] = value # Convert JSON object to dictionary.

    for i in range(len(architecture)): # Iterate through architecture.json.
        if architecture[i]["type"] in catalog_types_cost: # First, check if the architecture type is in the catalog_types_cost dictionary.
            # If yes, calculate the itemized cost by multiplying the hours by the corresponding type cost from catalog_types_cost.
            itemized_cost = architecture[i]["hours"] * catalog_types_cost[architecture[i]["type"]]
            # Add all the itemized costs to the itemized_costs string.
            itemized_costs += architecture[i]["name"] + ": $" "%.2f" % itemized_cost + "\n"
        else: # If the architecture type is not in the catalog.json file, print an error message and add it to the itemized_costs string.
            print("Error: " + architecture[i]["type"] + " is not in the catalog.")
            itemized_costs += "Error: " + architecture[i]["name"] + " is not in the catalog.\n"

    # Return the itemized_costs string.
    return "Itemized Costs:\n" + itemized_costs + "\n"

# Function to calculate total cost.
def calculate_total_cost(catalog_file, architecture_file):
    catalog = load_json_files(catalog_file)
    architecture = load_json_files(architecture_file)

    catalog_types_cost = {} # Define a dictionary to store catalog types and their corresponding costs.
    total_cost = 0

    for key, value in catalog.items():
        catalog_types_cost[key] = value # Convert JSON object to dictionary.

    for i in range(len(architecture)):
        if architecture[i]["type"] in catalog_types_cost: # Check if the architecture type is in the catalog_types_cost dictionary.
            # If yes, add the hours * cost to the total_cost variable.
            total_cost += architecture[i]["hours"] * catalog_types_cost[architecture[i]["type"]]

    # Return the total cost.
    return total_cost

# Function to get the current project ID using gcloud CLI.
def get_cloud_context():
    # Use subprocess to run the gcloud config command and capture the output.
    current_project_id = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True)
    # Return the project ID as a string using stdout.strip() to remove any trailing newline characters.
    return current_project_id.stdout.strip()

# Function to obtain the project budget using gcloud CLI.
def obtain_project_budget():
    # Use subprocess to run the gcloud billing budgets list command and capture the output.
    project_budget_amount = subprocess.run(["gcloud", "billing", "budgets", "list",
                                            "--billing-account=01689F-2FC313-8F3470",
                                            "--filter=budgetFilter.projects:projects/123478758390"],
                                           capture_output=True, text=True).stdout

    # Trim the output to only include the budget amount and load it into a YAML object.
    project_budget_amount_yaml = yaml.safe_load(project_budget_amount[4:][:-566])
    # Convert the YAML object to a JSON object.
    project_budget_amount_json = json.dumps(project_budget_amount_yaml, indent=2)
    # Load the JSON object into a Python dictionary.
    result = json.loads(project_budget_amount_json)
    # Return the budget amount as a string.
    return result['amount']['specifiedAmount']['units']

# Function to write the cost report to a text file.
def write_cost_report():
    # Write the cost report to a text file named cost_report.txt.
    with open("cost_report.txt", "w") as file:
        file.write("Cost Report\n")
        file.write("===========\n\n")
        file.write("Billing Account ID: " + BILLING_ACCOUNT_ID + "\n") # Add Billing Account ID to the report.
        file.write("Project ID: " + get_cloud_context() + "\n\n") # Add Project ID to the report.
        file.write(calculate_itemized_cost(CATALOG_FILE_PATH, ARCHITECTURE_FILE_PATH)) # Calculate and add itemized costs to the report.
        # Calculate and add the total cost to the report, comparing it to the project budget.
        file.write("Total Projected Cost: $%.2f" % calculate_total_cost(CATALOG_FILE_PATH, ARCHITECTURE_FILE_PATH) + " v.s Project Budget: $" + obtain_project_budget())
        # Check if the total cost is less than or equal to the project budget.
        if calculate_total_cost(CATALOG_FILE_PATH, ARCHITECTURE_FILE_PATH) <= float(obtain_project_budget()):
            # If yes, add "APPROVED" to the report.
            file.write("\nStatus: APPROVED\n")
        else:
            # If not, add "REJECTED" to the report.
            file.write("\nStatus: REJECTED\n")

# Main function to execute the script.
if __name__ == "__main__":
    write_cost_report()