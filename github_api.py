from urllib import response

import requests
import os
import logging 
from datetime import datetime

#Get token from environment variable (never hardcoded)
token = os.environ.get("GITHUB_TOKEN")

#Define headers
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com"

logging.basicConfig(
    filename="github_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log_action(action, result):
    username_response = requests.get(f"{BASE_URL}/user", headers=headers)
    username = username_response.json().get('login', 'unknown')
    logging.info(f"User: {username} | Action: {action} | Result: {result}")

#aestethics lol
def divider():
    print("=" * 40)

#Account Summary
def view_account_summary():
    try:
        response = requests.get(f"{BASE_URL}/user", headers=headers)
        response.raise_for_status()
        data = response.json()
        divider()
        print("          GITHUB ACCOUNT SUMMARY")
        divider()
        print(f"     Username:    {data['login']}")
        print(f"     Account ID:  {data['id']}")
        print(f"     Account Type:  {data['type']}")
        print(f"     Public Repos:  {data['public_repos']}")
        print(f"     Private Repos: {data.get('total_private_repos', 'N/A')}")
        print(f"     Followers:     {data['followers']}")
        print(f"     Following:     {data['following']}")
        print(f"     Created At:   {data['created_at']}")
        print(f"     2FA Enabled:    {data.get('two_factor_authentication', 'N/A')}")
        divider()
    except requests.exceptions.ConnectionError:
        print("  ❌ No internet connection. Please check your network.")
        logging.error("Action: VIEW_ACCOUNT | Result: ConnectionError")
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP Error: {e}")
        logging.error(f"Action: VIEW_ACCOUNT | Result: HTTPError - {e}")

#List Repositories
def list_repositories():
    response = requests.get(f"{BASE_URL}/user/repos", headers=headers)
    repos = response.json()
    divider()
    print("          YOUR REPOSITORIES")
    divider()
    for repo in repos:
        visibility = "Private" if repo['private'] else "Public"
        print(f"       {repo['name']}")
        print(f"       Visibility: {visibility}")
        print(f"       URL: {repo['html_url']}")
        print(f"        Created At: {repo['created_at'][:10]}")
        print()
    divider()

#Creating a Repository
def create_repository():
    divider()
    print("          CREATE NEW REPOSITORY")
    divider()
    name = input("Enter repository name: ")
    description = input("Enter repository description (optional): ")
    private_input = input("  Private? (yes/no): ").strip().lower()
    private = private_input == "yes"

    body = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": True
    }

    response = requests.post(
        f"{BASE_URL}/user/repos",
        headers=headers,
        json=body
    )

    if response.status_code == 201:
        print("Repository created successfully!")
        username_response = requests.get(f"{BASE_URL}/user", headers=headers)
        username = username_response.json().get('login', 'unknown')
        logging.info(f"User: {username} | Action: CREATE_REPO | Result: Success - {name}")
    else:
        print(f"\n  ❌ Error {response.status_code}: {response.json()['message']}")
        username_response = requests.get(f"{BASE_URL}/user", headers=headers)
        username = username_response.json().get('login', 'unknown')
        logging.error(f"User: {username} | Action: CREATE_REPO | Result: Failed - {response.status_code}")

def delete_repository():
    divider()
    print("          DELETE A REPOSITORY")
    divider()
    username_response = requests.get(f"{BASE_URL}/user", headers=headers)
    username = username_response.json()['login']

    name = input("Enter repository name to delete: ")
    confirm = input(f"Are you sure you want to delete '{name}'? This action cannot be undone! (yes/no): ").strip().lower()

    if confirm.lower() != "yes":
        print("Deletion cancelled.")
        divider()
        return
    
    response = requests.delete(
        f"{BASE_URL}/repos/{username}/{name}",
        headers=headers
    )

    if response.status_code == 204:
        print("Repository deleted successfully!")
        logging.info(f"User: {username} | Action: DELETE_REPO | Result: Success - {name}")
    else:
        print(f"\n  ❌ Error {response.status_code}: {response.json()['message']}")
        logging.error(f"User: {username} | Action: DELETE_REPO | Result: Failed - {response.status_code}")
        divider()

def check_2fa_status():
    response = requests.get(f"{BASE_URL}/user", headers=headers)
    data = response.json()
    divider()
    print("         2FA STATUS CHECK")
    divider()
    status = data['two_factor_authentication']
    if status:
        print(f"  ✅ 2FA is ENABLED on {data['login']}'s account")
    else:
        print(f"  🚨 WARNING: 2FA is DISABLED on {data['login']}'s account")
        print("  Action required: Enable at github.com/settings/security")
    divider()

def main():
    while True:
        print()
        divider()
        print("     GITHUB IAM AUTOMATION TOOL")
        divider()
        print("  1. View Account Summary")   
        print("  2. List My Repositories")
        print("  3. Create New Repository")
        print("  4. Delete a Repository")
        print("  5. Check 2FA Status")
        print("  6. Exit")
        divider()

        choice = input("   Enter your choice (1-6): ").strip()

        if choice == "1":
            view_account_summary()
        elif choice == "2":
            list_repositories()
        elif choice == "3":
            create_repository()
        elif choice == "4":
            delete_repository()
        elif choice == "5":
            check_2fa_status()          
        elif choice == "6":
            print("\n Exiting... Goodbye!")
            break
        else:
            print("\n  Invalid choice. Please enter a number between 1 and 6.")
        
if __name__ == "__main__":
    main()