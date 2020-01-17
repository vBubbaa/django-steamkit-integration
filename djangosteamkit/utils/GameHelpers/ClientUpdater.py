from Client import Client

client = Client()
client.login()

# Used to get the initial build current change number to pick up on
currentChangeNum = client.get_changes(1).current_change_number

## TODO:
##  - Function to loop every minute to check for new changes
##  - Set the current change number to the new current change number
changes = client.get_changes(7562810)
print(changes)
