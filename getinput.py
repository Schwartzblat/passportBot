from single import get_locations


def get_input():
    locations = get_locations()
    id = input("Enter your id number: ")
    phone_number = input("Enter your phone number: ")
    for i in range(len(locations)):
        print(str(i), locations[i]['LocationName'])

    locations_list = []
    print("Enter the numbers of the wanted locations. if you want to stop type 'quit': ")
    to_continue = input()
    while to_continue != "quit":
        try:
            locations_num_list.append(locations[int(to_continue)])
        except ValueError:
            print("Invalid input")
        to_continue = input()
    info_dict = {
        "id": id,
        "phone_number": phone_number,
        "locations_numbers": locations_list
    }
    return info_dict


if __name__ == '__main__':
    print(get_input())