import re
from typing import List, Union, Dict, Any

def _get_student_attr(student: Union[Dict[str, Any], Any], field: str):
    if isinstance(student, dict):
        return student[field]
    return getattr(student, field)

def insertion_sort_by_field(students: List[Any], field: str) -> List[Any]:
    """
    Manually implemented Insertion Sort in-place on students list.
    Outer loop starts at index 1, inner while loop shifts larger elements right.
    Does NOT use built-in sort() or sorted().
    """
    for i in range(1, len(students)):
        key_item = students[i]
        key_val = _get_student_attr(key_item, field)
        j = i - 1
        while j >= 0 and _get_student_attr(students[j], field) > key_val:
            students[j + 1] = students[j]
            j -= 1
        students[j + 1] = key_item
    return students

def binary_search_by_name(sorted_by_name_list: List[Any], name: str) -> Union[Any, int]:
    """
    Manually implemented iterative Binary Search by name.
    Uses mid = low + (high - low) // 2.
    Returns matching student record or -1 if not found.
    """
    low = 0
    high = len(sorted_by_name_list) - 1
    target_name = name.strip()

    while low <= high:
        mid = low + (high - low) // 2
        current_student = sorted_by_name_list[mid]
        curr_name = _get_student_attr(current_student, "name")

        if curr_name == target_name:
            return current_student
        elif curr_name < target_name:
            low = mid + 1
        else:
            high = mid - 1
    return -1

def format_roster_report(students: List[Any]) -> str:
    """
    Formats roster report with one line per student:
    [Age 22] Aditi Rao <aditi.rao@example.com>
    """
    lines = []
    for s in students:
        age = _get_student_attr(s, "age")
        name = _get_student_attr(s, "name")
        email = _get_student_attr(s, "email")
        lines.append(f"[Age {age}] {name} <{email}>")
    return "\n".join(lines)

def count_students_meeting_min_age(students: List[Any], min_age: int) -> int:
    """
    Counts students with age >= min_age using an accumulator variable.
    """
    count = 0
    for s in students:
        age = _get_student_attr(s, "age")
        if age >= min_age:
            count += 1
    return count
