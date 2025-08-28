def remove_objects(objects_to_remove, object_list):
    if isinstance(object_list, list):
        for obj in objects_to_remove:
            if obj in object_list:
                object_list.remove(obj)
    elif isinstance(object_list, dict):
        objects_to_remove_set = set(objects_to_remove)

        for sector, obj_list in object_list.items():
            object_list[sector] = [a for a in obj_list if a not in objects_to_remove_set]
