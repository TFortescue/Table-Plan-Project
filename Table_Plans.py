import csv
import math

# --- Constants for Scoring Penalties/Bonuses ---
# These are settings for how to score table plans. Lower scores are better.
BONUS_PREFERRED = -1000
PENALTY_RELATION = 100
PENALTY_SEX_VIOLATION = 50
# PENALTY_REPEAT_NEIGHBOUR = float('inf') # A very big penalty for repeated neighbours
# PENALTY_SECOND_SEX_VIOLATION = float('inf') # A very big penalty for too many same-sex pairs


# --- Data Structures ---

class Person:
    """Stores info about a person."""
    def __init__(self, name, sex, relations, preferred, meals):
        """Make a new Person. Sex must be 'male' or 'female'."""
        if sex not in ('male', 'female'):
             raise ValueError(f"Invalid sex '{sex}' for person '{name}'. Must be 'male' or 'female'.")
        self.name = name
        self.sex = sex
        self.relations = list(relations) # Store as a list
        self.preferred = list(preferred) # Store as a list
        self.meals = meals

    def __repr__(self):
        return (f"Person(name='{self.name}', sex='{self.sex}', "
                f"relations={self.relations}, preferred={self.preferred}, meals={self.meals})")

    def is_related_to(self, other_person):
        """Is this person related to the other person?"""
        return other_person.name in self.relations

    def prefers(self, other_person):
        """Does this person want to sit with the other person?"""
        return other_person.name in self.preferred


# --- CSV Data Loading ---

def read_people_from_csv(filename):
    """Read people's details from a CSV file."""
    people = []
    required_headers = ["name", "sex", "relations", "preferred people"]
    line_count = 0
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            line_count = 1 # header is first line

            if not headers:
                print(f"Error: CSV file '{filename}' seems empty or has no headers.")
                return []

            # Check for important headers
            missing_headers = []
            for h in required_headers:
                if h not in headers:
                    missing_headers.append(h)
            if missing_headers:
                print(f"Error: CSV file '{filename}' is missing important columns like '{missing_headers[0]}'.")
                return []

            # Find out which columns are for meals
            meal_columns = []
            try:
                preferred_idx = headers.index('preferred people')
                meal_columns = headers[preferred_idx + 1:]
                if not meal_columns:
                    print("Warning: No meal columns found after 'preferred people' column in CSV.")
            except ValueError:
                 print("Error: 'preferred people' column was not found. Cannot find meal columns.")
                 return []

            # Read each person's info
            for row_data in reader:
                line_count += 1
                try:
                    name = row_data.get('name', '').strip()
                    sex = row_data.get('sex', '').strip().lower()

                    if not name or not sex: # Need name and sex
                        print(f"Warning: Skipping line {line_count} because name or sex is missing.")
                        continue

                    relations_str = row_data.get('relations', '')
                    relations_list = []
                    for r_item in relations_str.split(','):
                        r_stripped = r_item.strip()
                        if r_stripped: # only add if not empty after stripping
                            relations_list.append(r_stripped)

                    preferred_str = row_data.get('preferred people', '')
                    preferred_list = []
                    for p_item in preferred_str.split(','):
                        p_stripped = p_item.strip()
                        if p_stripped:
                            preferred_list.append(p_stripped)

                    # Determine meal attendance
                    attended_meals = []
                    for col_name in meal_columns:
                        # Use the full column name (stripped) as the meal ID
                        meal_id = col_name.strip() 

                        if meal_id and row_data.get(col_name, '').strip().lower() == "yes": # Ensure meal_id is not empty
                            attended_meals.append(meal_id)
                    
                    # Make a new Person object and add to list
                    new_person = Person(name, sex, relations_list, preferred_list, attended_meals)
                    people.append(new_person)

                except ValueError as ve_err: # Problem with the data for a person
                     print(f"Warning: Skipping line {line_count} due to bad data: {ve_err}")
                     continue
                except Exception: # Any other problem with this row
                     print(f"Warning: Error processing line {line_count}.")
                     continue

    except FileNotFoundError:
        print(f"Error: Cannot find the file: {filename}")
        return []
    except Exception: # Any other problem opening or reading the file
        print(f"An error happened while reading the file {filename}.")
        return []

    return people


def read_meals_from_csv(filename):
    """Get all meal names from the CSV file's header."""
    meal_ids = []
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile) # Use  csv.reader for header
            header_row = next(reader, None) # Get the first line (header)

            if not header_row:
                print(f"Error: Cannot read header from CSV file '{filename}'.")
                return []

            try: # Find where 'preferred people' column is
                preferred_idx = header_row.index('preferred people')
            except ValueError:
                print("Error: CSV header missing 'preferred people' column.")
                return []

            # Meal columns are after 'preferred people'
            meal_columns_names = header_row[preferred_idx + 1:]
            for col_name_full in meal_columns_names:
                 # Use the full column name (stripped) as the meal ID
                 meal_id_val = col_name_full.strip()
                 
                 if meal_id_val: # Add if not empty
                    meal_ids.append(meal_id_val)

    except FileNotFoundError:
        print(f"Error: Cannot find file: {filename}")
        return []
    except Exception:
        print(f"An error happened while reading meal names from {filename}.")
        return []
    return meal_ids


# --- Arrangement Logic Helpers ---

def are_arrangements_same(arr1, arr2):
    """Are these two table plans the same (even if rotated)?"""
    n1 = len(arr1)
    n2 = len(arr2)
    if n1 != n2: return False # Different number of people
    if n1 == 0: return True # Empty plans are the same

    try:
        first_person_arr1 = arr1[0] # Get the first person from first plan
        
        # Find where this person is in the second plan
        possible_starts_in_arr2 = []
        for i, p in enumerate(arr2):
            if p.name == first_person_arr1.name:
                possible_starts_in_arr2.append(i)

        if not possible_starts_in_arr2: return False # First person not even in second plan

        # Check each possible starting point
        for start_idx in possible_starts_in_arr2:
            is_a_match = True
            for i in range(n1): # Compare all people in order
                person_from_arr1 = arr1[i]
                person_from_arr2 = arr2[(start_idx + i) % n1] # % n1 handles wrap-around
                if person_from_arr1.name != person_from_arr2.name:
                    is_a_match = False # Mismatch found
                    break
            if is_a_match:
                return True # Found a rotational match
        
        return False # No rotational match found
    except Exception: # Something unexpected went wrong
        return False


# --- Core Backtracking Algorithm ---

def _get_candidate_score(candidate):
    """Get score from candidate tuple for sorting."""
    return candidate[0] # Score is the first item

def _find_arrangement_backtrack(
    current_arrangement,
    remaining_people, # A set of people still to seat
    total_people_to_seat,
    arrangements_already_found_for_this_meal,
    seated_neighbour_pairs_overall, # Pairs seated together in any meal so far
    sex_violation_already_used_up
):
    """Try to find a good table plan by adding one person at a time."""
    
    num_people_placed = len(current_arrangement)

    # Base Case: If all people are placed
    if num_people_placed == total_people_to_seat:
        first_person = current_arrangement[0]
        last_person = current_arrangement[-1]

        # Check pair: last person and first person
        name1 = last_person.name
        name2 = first_person.name
        if name1 < name2:
            final_pair = (name1, name2)
        else:
            final_pair = (name2, name1)

        if final_pair in seated_neighbour_pairs_overall: # Was this pair already a neighbour?
            return None # Not allowed

        # Check for second same-sex pair if first person and last person are same sex
        if last_person.sex == first_person.sex and sex_violation_already_used_up:
            return None # Not allowed

        # Check if this exact arrangement (or a rotation) was already found for this meal
        is_rotation_of_existing = False
        for prev_arr in arrangements_already_found_for_this_meal:
            if are_arrangements_same(current_arrangement, prev_arr):
                is_rotation_of_existing = True
                break
        if is_rotation_of_existing:
            return None
        
        return current_arrangement # This arrangement is complete and valid

    # Recursive Step: Try adding another person
    person_seated_last = None
    if num_people_placed > 0:
        person_seated_last = current_arrangement[-1]
    
    possible_next_people = [] 

    for person_to_try in remaining_people:
        current_score = 0
        is_not_allowed = False # Flag for hard rule violations
        will_cause_sex_violation_now = False

        if person_seated_last: # If this isn't the first person being placed
            # Create canonical pair for checking
            name1 = person_seated_last.name
            name2 = person_to_try.name
            if name1 < name2:
                current_pair = (name1, name2)
            else:
                current_pair = (name2, name1)

            if current_pair in seated_neighbour_pairs_overall: # Check hard constraint: repeat neighbour
                is_not_allowed = True

            # Check sex violation
            if not is_not_allowed and person_seated_last.sex == person_to_try.sex:
                if sex_violation_already_used_up: # Already used our one allowed same-sex pair
                    is_not_allowed = True 
                else: # This would be the first (and only allowed) same-sex pair
                    will_cause_sex_violation_now = True
                    current_score += PENALTY_SEX_VIOLATION # Add penalty for using it

            # Calculate scores if still a valid option
            if not is_not_allowed:
                if person_seated_last.is_related_to(person_to_try) or person_to_try.is_related_to(person_seated_last):
                     current_score += PENALTY_RELATION
                if person_seated_last.prefers(person_to_try) or person_to_try.prefers(person_seated_last):
                     current_score += BONUS_PREFERRED 
        
        if not is_not_allowed: # If person can be added
            possible_next_people.append((current_score, person_to_try, will_cause_sex_violation_now))

    # Sort people to try by score (lower is better)
    possible_next_people.sort(key=_get_candidate_score)

    # Try each person from the sorted list
    for score, person_added, creates_violation_this_step in possible_next_people:
        
        remaining_after_this_add = remaining_people - {person_added} # Update set of remaining people
        
        new_sex_violation_status = sex_violation_already_used_up or creates_violation_this_step

        # Recursive call
        found_plan = _find_arrangement_backtrack(
            current_arrangement + [person_added], # Add person to current plan
            remaining_after_this_add,
            total_people_to_seat,
            arrangements_already_found_for_this_meal,
            seated_neighbour_pairs_overall,
            new_sex_violation_status
        )
        if found_plan: # If the recursive call found a complete plan
            return found_plan 

    return None # No person led to a solution from this state


# --- Main Assembly Function ---

def seat_people(all_people_info, meal_names_list):
    """Figure out seating plans for all meals."""
    
    final_seating_arrangements = {} # Store plans here: meal_name -> list of plans
    
    # Keep track of pairs who have sat together in any meal
    # This is a set of (name1, name2) tuples where name1 < name2
    all_seated_neighbour_pairs_globally = set() 

    for meal_name in meal_names_list:
        # Find who is attending this meal
        attendees_this_meal = []
        for p in all_people_info:
            if meal_name in p.meals:
                attendees_this_meal.append(p)
        
        num_attendees_for_this_meal = len(attendees_this_meal)
        print(f"\nTrying to make a plan for Meal '{meal_name}' with {num_attendees_for_this_meal} people...")

        if num_attendees_for_this_meal == 0:
            print("  No one is attending this meal.")
            final_seating_arrangements[meal_name] = []
            continue
        if num_attendees_for_this_meal == 1:
             print("  Only one person, so no seating plan needed.")
             final_seating_arrangements[meal_name] = [attendees_this_meal] # Plan is just the one person
             continue

        # Get any arrangements already found for THIS meal (for rotation check)
        arrangements_found_for_this_meal_before_this_try = final_seating_arrangements.get(meal_name, [])

        # Try to find one arrangement
        current_best_arrangement = _find_arrangement_backtrack(
            [], # Start with empty table
            set(attendees_this_meal), # People to seat for this meal
            num_attendees_for_this_meal,
            arrangements_found_for_this_meal_before_this_try,
            all_seated_neighbour_pairs_globally, 
            False # Reset: no sex violation used yet for this attempt
        )

        if current_best_arrangement: # If a plan was found
            print(f"  Found a plan for Meal '{meal_name}'.")
            
            # Add to our dictionary of plans
            if meal_name not in final_seating_arrangements:
                final_seating_arrangements[meal_name] = []
            final_seating_arrangements[meal_name].append(current_best_arrangement)

            # Update the global list of who sat next to whom
            for i in range(num_attendees_for_this_meal):
                p1 = current_best_arrangement[i]
                p2 = current_best_arrangement[(i + 1) % num_attendees_for_this_meal]
                
                # Create canonical pair
                name_p1 = p1.name
                name_p2 = p2.name
                if name_p1 < name_p2:
                    new_pair = (name_p1, name_p2)
                else:
                    new_pair = (name_p2, name_p1)
                all_seated_neighbour_pairs_globally.add(new_pair)
        else: # No plan found
            print(f"  Could not find a good plan for Meal '{meal_name}'.")
            if meal_name not in final_seating_arrangements: # Make sure meal key exists
                 final_seating_arrangements[meal_name] = []

    return final_seating_arrangements


# --- Visualisation ---

def draw_text_table(arrangement_list, grid_width=60, grid_height=25):
    """Draw the table plan as text art."""
    num_people = len(arrangement_list)
    if num_people == 0: return

    # Make empty grid
    grid = []
    for r_num in range(grid_height):
        new_row_for_grid = []
        for c_num in range(grid_width):
            new_row_for_grid.append(' ')
        grid.append(new_row_for_grid)

    centre_coord_x, centre_coord_y = grid_width // 2, grid_height // 2
    # How big the circle is
    radius_for_x = (grid_width // 2) * 0.8
    radius_for_y = (grid_height // 2) * 0.7

    # Place each person
    for i, person_details in enumerate(arrangement_list):
        angle = (2 * math.pi * i / num_people) - (math.pi / 2) # Angle for person i
        # Calculate x, y position on the circle
        x_pos = centre_coord_x + radius_for_x * math.cos(angle)
        y_pos = centre_coord_y + radius_for_y * math.sin(angle)
        # Convert to grid row and column
        grid_row = int(round(y_pos))
        grid_col = int(round(x_pos))

        # Make sure it's inside the grid
        grid_row = max(0, min(grid_height - 1, grid_row))
        grid_col = max(0, min(grid_width - 1, grid_col))

        # Make the label text (e.g., "1:Tom   ")
        person_label = f"{i+1}:{person_details.name[:6]}" 
        label_length = len(person_label)
        # Try to centre the label
        start_column_for_label = max(0, grid_col - label_length // 2) 
        
        # Make sure label doesn't go off edge of grid
        visible_part_of_label = person_label[:grid_width - start_column_for_label] 

        try:
            # Check if space for label is free
            space_is_free = True
            if start_column_for_label + len(visible_part_of_label) <= grid_width:
                for k_offset in range(len(visible_part_of_label)):
                    if grid[grid_row][start_column_for_label + k_offset] != ' ':
                        space_is_free = False
                        break
            else: # Label would go out of bounds
                space_is_free = False
            
            if space_is_free: # If free, write label
                for k, char_to_write in enumerate(visible_part_of_label):
                    grid[grid_row][start_column_for_label + k] = char_to_write
            elif grid[grid_row][grid_col] == ' ': # Else, if exact spot is free, put a star
                grid[grid_row][grid_col] = '*'
        except IndexError: 
             pass # Should not happen due to clamping, but just in case

    # Print the grid with a border
    top_bottom_border = "+" + "-" * (grid_width - 2) + "+"
    print(f"  {top_bottom_border}")
    for current_row_data in grid:
        print(f" |{''.join(current_row_data[1:-1])}|") 
    print(f"  {top_bottom_border}")


def visualize_seating(all_meal_arrangements):
    """Show all the seating plans that were made."""
    print("\n--- Final Seating Arrangements ---")
    
    # Check if any plans were made at all
    any_plans_made = False
    if all_meal_arrangements: # If the dictionary is not empty
        for list_of_plans_for_a_meal in all_meal_arrangements.values():
            if list_of_plans_for_a_meal: # If there's at least one plan for one meal
                any_plans_made = True
                break
    
    if not any_plans_made:
        print("No valid seating arrangements were generated.")
        return

    # Keep track of pairs shown so we can mark repeats in the list view
    pairs_shown_in_list_view = set() 

    for meal_name, list_of_arrangements_for_meal in all_meal_arrangements.items():
        print(f"\nMeal '{meal_name}':")
        if not list_of_arrangements_for_meal: # No plans for this meal
            print("  No arrangement found.")
            continue

        # Show the latest (usually only) arrangement for this meal
        current_arrangement_to_show = list_of_arrangements_for_meal[-1]
        num_people_in_arrangement = len(current_arrangement_to_show)
        if num_people_in_arrangement == 0: continue

        print("\n  List View:")
        num_same_sex_violations_in_this_plan = 0
        pairs_in_this_specific_meal_plan = set()
        # For noting what symbols mean
        legend_notes_needed = {'P': False, 'N': False, 'R': False, 'S': False} 

        # Show who sits next to whom
        for i in range(num_people_in_arrangement):
            person_A = current_arrangement_to_show[i]
            person_B = current_arrangement_to_show[(i + 1) % num_people_in_arrangement] # Next person, wraps around
            
            # Create canonical pair key
            name1 = person_A.name
            name2 = person_B.name
            if name1 < name2:
                pair_as_key = (name1, name2)
            else:
                pair_as_key = (name2, name1)
            pairs_in_this_specific_meal_plan.add(pair_as_key)

            # Check for special conditions for indicators
            is_relation_pair = person_A.is_related_to(person_B) or person_B.is_related_to(person_A)
            is_preferred_pair = person_A.prefers(person_B) or person_B.prefers(person_A)
            # Was this exact pair seen as neighbours in a PREVIOUS meal's list view?
            is_repeated_neighbour_from_another_meal = pair_as_key in pairs_shown_in_list_view
            is_same_sex_pair = person_A.sex == person_B.sex

            # Build indicator string like (P*) (R!)
            indicator_symbols = ""
            if is_preferred_pair: indicator_symbols += " (P*)"; legend_notes_needed['P'] = True
            if is_repeated_neighbour_from_another_meal: indicator_symbols += " (N!)"; legend_notes_needed['N'] = True
            if is_relation_pair: indicator_symbols += " (R!)"; legend_notes_needed['R'] = True
            if is_same_sex_pair:
                indicator_symbols += " (S!)"; legend_notes_needed['S'] = True
                # Count unique same-sex pairs for the summary note
                if i < (i + 1) % num_people_in_arrangement or num_people_in_arrangement == 2: 
                    num_same_sex_violations_in_this_plan += 1
            
            # Print the seating pair
            print(f"    Seat {i + 1}: {person_A.name} ({person_A.sex}){indicator_symbols}"
                  f" -> Seat {(i + 1) % num_people_in_arrangement + 1}: {person_B.name} ({person_B.sex})")

        # Print legend for symbols, if any were used
        notes_for_legend = []
        if legend_notes_needed['P']: notes_for_legend.append("(P*) = Preferred")
        if legend_notes_needed['N']: notes_for_legend.append("(N!) = Repeated Neighbour Pair (from a previous meal)")
        if legend_notes_needed['R']: notes_for_legend.append("(R!) = Related")
        if legend_notes_needed['S']:
            plural_s = 's' if num_same_sex_violations_in_this_plan != 1 else ''
            notes_for_legend.append(f"(S!) = {num_same_sex_violations_in_this_plan} Same-sex Pair{plural_s}")
        if notes_for_legend:
             print(f"    (Note: {'; '.join(notes_for_legend)})")

        # Add pairs from this meal to the overall set for next meal's (N!) check
        pairs_shown_in_list_view.update(pairs_in_this_specific_meal_plan)

        print("\n  Visual Layout:")
        draw_text_table(current_arrangement_to_show)


# --- Script Start Point ---

def main():
    """Run the seating plan program."""
    print("Seating Plan Generator")
    print("Needs a CSV file with: name, sex (male/female), relations, preferred people, meal 1, ...")
    
    try:
        csv_file_name = input("Enter the CSV file name: ")
    except EOFError: # If user presses Ctrl+D
        print("\nNo input given. Exiting.")
        return

    print(f"\nReading data from: {csv_file_name}")
    
    list_of_people = read_people_from_csv(csv_file_name)
    if not list_of_people: # If list is empty
        print("Could not load people data. Check the file and format. Exiting.")
        return

    list_of_meals = read_meals_from_csv(csv_file_name)
    if not list_of_meals:
         print("Could not get meal names from CSV. Check 'preferred people' column. Exiting.")
         return

    print(f"Data loaded: {len(list_of_people)} people, {len(list_of_meals)} meals ({', '.join(list_of_meals)}).")

    # Get the seating plans
    arranged_seatings = seat_people(list_of_people, list_of_meals)

    # Show the results
    visualize_seating(arranged_seatings)

    print("\nGeneration complete.")


if __name__ == "__main__":
    main() 