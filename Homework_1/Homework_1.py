import json
import subprocess
import yaml

BILLING_ACCOUNT_ID = "01689F-2FC313-8F3470"
CATALOG_FILE_PATH = "/Users/rstoffel/PycharmProjects/CSC323/Homework_1/JSON/catalog.json"
ARCHITECTURE_FILE_PATH = "/Users/rstoffel/PycharmProjects/CSC323/Homework_1/JSON/architecture.json"

def load_json_files(file_name):
    with open(file_name, "r") as file:
        return json.load(file)

def calculate_itemized_cost(catalog_file, architecture_file):
    catalog = load_json_files(catalog_file)
    architecture = load_json_files(architecture_file)

    catalog_types_cost = {}
    itemized_costs = ""
    for key, value in catalog.items():
        catalog_types_cost[key] = value

    for i in range(len(architecture)):
        if architecture[i]["type"] in catalog_types_cost:
            itemized_cost = architecture[i]["hours"] * catalog_types_cost[architecture[i]["type"]]
            itemized_costs += architecture[i]["name"] + ": $" "%.2f" % itemized_cost + "\n"
        else:
            print("Error: " + architecture[i]["type"] + " is not in the catalog.")
            itemized_costs += "Error: " + architecture[i]["name"] + " is not in the catalog.\n"

    return "Itemized Costs:\n" + itemized_costs + "\n"

def calculate_total_cost(catalog_file, architecture_file):
    catalog = load_json_files(catalog_file)
    architecture = load_json_files(architecture_file)

    total_cost = 0

    catalog_types_cost = {}
    for key, value in catalog.items():
        catalog_types_cost[key] = value

    for i in range(len(architecture)):
        if architecture[i]["type"] in catalog_types_cost:
            total_cost += architecture[i]["hours"] * catalog_types_cost[architecture[i]["type"]]

    return total_cost

def get_cloud_context():
    current_project_id = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True)
    return current_project_id.stdout.strip()

def obtain_project_budget():
    project_budget_amount = subprocess.run(["gcloud", "billing", "budgets", "list", "--billing-account=01689F-2FC313-8F3470", "--filter=budgetFilter.projects:projects/123478758390"], capture_output=True, text=True).stdout
    project_budget_amount_yaml = yaml.safe_load(project_budget_amount[4:][:-566])
    project_budget_amount_json = json.dumps(project_budget_amount_yaml, indent=2)
    result = json.loads(project_budget_amount_json)
    return result['amount']['specifiedAmount']['units']
def write_cost_report():
    with open("cost_report.txt", "w") as file:
        file.write("Cost Report\n")
        file.write("===========\n\n")
        file.write("Billing Account ID: " + BILLING_ACCOUNT_ID + "\n")
        file.write("Project ID: " + get_cloud_context() + "\n\n")
        file.write(calculate_itemized_cost(CATALOG_FILE_PATH, ARCHITECTURE_FILE_PATH))
        file.write("Total Projected Cost: $%.2f" % calculate_total_cost(CATALOG_FILE_PATH, ARCHITECTURE_FILE_PATH) + " v.s Project Budget: $" + obtain_project_budget())
        if calculate_total_cost(CATALOG_FILE_PATH, ARCHITECTURE_FILE_PATH) < float(obtain_project_budget()):
            file.write("\nStatus: APPROVED\n")
        else:
            file.write("\nStatus: REJECTED\n")
if __name__ == "__main__":
    write_cost_report()