from data.problem_list import problems


def check_list_uniqueness(items):
    # Quick uniqueness check using set: if lengths match, all items are unique.
    if len(items) == len(set(items)):
        print("All items in the list are unique!")
    else:
        print("There are duplicate items in the list.")

        # Detailed reporting: find and print duplicate items.
        seen = set()
        duplicates = set()
        for item in items:
            if item in seen:
                duplicates.add(item)
            else:
                seen.add(item)

        print("Duplicate items found:", list(duplicates))


if __name__ == '__main__':
    check_list_uniqueness(problems)
