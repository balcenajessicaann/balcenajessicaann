import requests  

student_id = input("Enter your Student ID: ")  
 
url = "https://abordaje-jm.onrender.com/grades"  
 
response = requests.get(url)  
 
if response.status_code == 200:  
    data = response.json()  

    print("Student ID:", data["student_id"])  
    print("Grades:")  

for subject, grade in data["grades"].items():  
    print(f"{subject}: {grade}")  

else:  
    print("Request failed.")  
    print("Status Code:", response.status_code)  