import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


base_url = "https://www.livetheelm.com/floor-plans/?bedroom=&type=&options=&minprice=&maxprice=&availability=&sort=unitrent&order=ASC&pagenumber={}"

# Variables to store the previous apartment data
previous_apartments = []

# Function to send a notification
def send_notification(apartment_name):
    # Close the SMTP connection
    print("New apartment added:", apartment_name)
    sender = "carlelgstrom@gmail.com"  # Replace with your email address
    recipient = "carlelgstrom@gmail.com"  # Replace with the recipient's email address
    subject = "New Apartment Notification"
    body = f"A new apartment has been added: {apartment_name}"

    message = Mail(
        from_email=sender,
        to_emails=recipient,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

# Function to fetch apartment data and check for new additions
def check_apartments():
    # Iterate through pagination pages
    for page_number in range(1, 6):  # Example: Fetching information from pages 1 to 5
        url = base_url.format(page_number)

        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the container that holds the apartment information
        apartment_container = soup.find("div", class_="fp-list")

        # Check if the container exists
        if apartment_container:
            # Find all apartment listings
            apartment_listings = apartment_container.find_all("div", class_="fp-list-item")

            # Iterate over each apartment listing and extract the information
            for apartment in apartment_listings:
                # Extract the apartment name
                name_element = apartment.find("span", class_="unit-title")
                name = name_element.text.strip() if name_element else "N/A"

                # Extract the apartment details
                details_elements = apartment.find_all("span", class_="unit-details")
                details = [detail.text.strip() for detail in details_elements]

                # Create a dictionary with the apartment information
                apartment_data = {
                    "name": name,
                    "details": details
                }

                # Check if the current apartment is new
                if apartment_data not in previous_apartments:
                    send_notification(name)  # Send notification for new apartmen
                else:
                    print("No new apartment found")

                # Add the apartment to the previous apartment list
                previous_apartments.append(apartment_data)

                # Print the apartment information
                print("Apartment:", name)
                for detail in details:
                    print("Detail:", detail)
                print("-" * 30)
        else:
            print("Apartment container not found.")

# Create a scheduler instance
scheduler = BlockingScheduler()

# Schedule the job to run every hour
scheduler.add_job(check_apartments, 'interval', minutes=1)

# Start the scheduler
scheduler.start()


