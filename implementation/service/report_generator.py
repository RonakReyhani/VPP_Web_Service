
# Main service: 
# gets the STDIN as an in put, gets the action and variables, 
#  for each action calls the relevant method from the utils

from utils.vpp_utils import VPPUtils
import json

def main():
    utils = VPPUtils()
    report_file = "vpp_report.json"
    print("Enter commands (one per line). Type 'Exit' to quit:")

    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue

            if line.lower() == "exit":
                utils.exit()
                break

            if ":" not in line:
                print("Invalid command format. Use Action: param1, param2, ...")
                continue

            action, params = line.split(":", 1)
            action = action.strip().lower()
            params = [p.strip() for p in params.split(",")]

            if action == "create vpp":
                name, revenue_percentage, daily_fee = params
                utils.create_update_vpp(name, float(revenue_percentage), float(daily_fee))
            elif action == "create site":
                vpp_name, nmi, address = params
                utils.create_update_site(vpp_name, nmi, address)
            elif action == "create battery":
                site_nmi, manufacturer, serial, capacity = params
                utils.create_update_battery(site_nmi, manufacturer, serial, float(capacity))
            elif action == "import events":
                file_path = params[0]
                utils.import_events(file_path)
            elif action == "create report":
                vpp_name, month_yyyy_mm = params
                report = utils.create_report(vpp_name, month_yyyy_mm)
                print(report)
                with open(report_file, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                    
            elif action == 'exit':
                utils.exit()
            else:
                print(f"Unknown action: {action}")
        except Exception as e:
            print(f"Error processing command: {e}")

if __name__ == "__main__":
    main()