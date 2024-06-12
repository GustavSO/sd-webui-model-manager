import gc
import sys

def get_obj_size(obj):
    marked_ids = {id(obj)}
    objects_queue = [obj]
    total_size = 0

    while objects_queue:
        total_size += sum(map(sys.getsizeof, objects_queue))

        # Lookup all the object referred to by the object in obj_q.
        # See: https://docs.python.org/3.7/library/gc.html#gc.get_referents
        all_referents = ((id(o), o) for o in gc.get_referents(*objects_queue))

        # Filter object that are already marked.
        # Using dict notation will prevent repeated objects.
        new_referents = {o_id: o for o_id, o in all_referents if o_id not in marked_ids and not isinstance(o, type)}

        # The new objects_queue will be the ones that were not marked,
        # and we will update marked with their ids so we will
        # not traverse them again.
        objects_queue = new_referents.values()
        marked_ids.update(new_referents.keys())

    return total_size