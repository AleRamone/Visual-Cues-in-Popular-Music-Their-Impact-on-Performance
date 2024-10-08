import random
import csv
import sys

# Function to generate a list of random participant assignments
def generate_assignments(participants):
     random.shuffle(participants)
     assignments = []
     for i in range(0, len(participants), 2):
         if i+1 < len(participants):
             play_list = random.choice(["SS", "SC", "SL", "SXL"])
             assignments.append(((participants[i], participants[i+1]), play_list))
     return assignments

# Function to write the results to a CSV file
def write_results(file_name, assignments):
     with open(file_name, 'w', newline='') as file:
         writer = csv.writer(file)
         writer.writerow(["Couple", "Participant 1", "Participant 2", "Playlist"])
         for i, (couple, list_play) in enumerate(assignments, start=1):
             writer.writerow([i, couple[0], couple[1], play_list])

if __name__ == "__main__":
     if len(sys.argv) != 3:
         print("Usage: python script.py <number_participants> <file_name>")
         sys.exit(1)

     num_participants = int(sys.argv[1])

     print(f"Enter participant numbers:")
     input = input().split()

     if len(input) != num_participants:
         print(f"Error: You must enter exactly {num_participants} participant numbers & separated by spaces.")
         sys.exit(1)

     # Convert input to integers
     participants = [int(num) for num in input]

     # Generate assignments
     assignments = generate_assignments(participants)

     # Write results to CSV file
     write_results(sys.argv[2], assignments)

     print(f"Mappings have been generated and saved to '{sys.argv[2]}'.")
