import requests

url = "https://balcenajessicaann.onrender.com/profile"

try:
    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        data = response.json()

        print("Student Profile")
        print("Student ID:", data["student_id"])
        print("Name:", data["name"])
        print("Program:", data["program"])
        print("Year:", data["year"])
        print("Section:", data["section"])
        print("Email:", data["email"])
        print("Skills:", ", ".join(data["skills"]))
    else:
        print("Request failed.")
        print("Status Code:", response.status_code)

except requests.exceptions.RequestException as error:
    print("Connection error:", error)
