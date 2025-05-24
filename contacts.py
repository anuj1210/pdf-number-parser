# Dictionary to store phone numbers and corresponding names
CONTACTS = {
    "9945194909": "Sandeep",  # Make sure this entry exists
    # Add more contacts here in the format "phone_number": "name"
}

def add_contact(phone_number, name):
    """Add or update a contact in the CONTACTS dictionary"""
    CONTACTS[phone_number] = name
    print(f"Added/Updated contact: {name} ({phone_number})")

def get_name_for_number(phone_number):
    """Get the name for a given phone number from the contacts dictionary"""
    name = CONTACTS.get(phone_number, "")
    print(f"Looking up {phone_number} -> {name}")  # Debug print
    return name

# Example usage:
if __name__ == "__main__":
    # Add some contacts
    add_contact("9945194909", "Sandeep")
    add_contact("9876543210", "John")
    
    # Test the contacts
    test_numbers = ["9945194909", "9876543210", "1234567890"]
    for number in test_numbers:
        name = get_name_for_number(number)
        if name:
            print(f"Number: {number}, Name: {name}")
        else:
            print(f"No name found for number: {number}") 