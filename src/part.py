import mido
import logger


def get_futur_partition(partition, i, target_time):
    futurpart = []
    l = i
    while partition[l]:
        if partition[l]["time"] > partition[i]["time"] + target_time:
            break
        futurpart.append(partition[l])
        l += 1
    return futurpart


def change_velocity(partition):
    """ The purpose of this function is to adjust the velocity for the visalisation
        The sound velocity wont be affected
    """
    i = 0
    while partition[i]:
        if partition[i]["msg"].type == "note_on":
            _time = partition[i]["time"]
            partition[i]["new_velocity"] = partition[i]["msg"].velocity
            velocity = partition[i]["msg"].velocity / 10
            l = i + 1
            while partition[l]:
                if partition[l]["time"] + 0.01 > _time + velocity:
                    break
                if partition[l]["msg"].type == "note_on":
                    if (
                        partition[l]["msg"].note == partition[i]["msg"].note
                        and partition[l]["msg"].channel == partition[i]["msg"].channel
                    ):
                        if _time + velocity > partition[l]["time"]:
                            if partition[l]["msg"].velocity == 0:
                                partition[l]["note_off"] = True
                            new_velocity = int(
                                (partition[l]["time"] - _time - 0.01) * 10
                            )
                            if new_velocity < 0.5:
                                new_velocity = 0.5
                            if new_velocity > velocity:
                                new_velocity = velocity
                            partition[i]["new_velocity"] = new_velocity
                            break
                l += 1
        i += 1
    return partition


def get_partition(mid, name):
    _time = 3
    partition = []
    for msg in mid:
        _time += msg.time
        if isinstance(msg, mido.MetaMessage):
            continue
        partition.append(
            {"time": _time, "msg": msg, "new_velocity": 0, "note_off": False}
        )
    partition.append(None)
    partition = change_velocity(partition)
    length = partition[-2]["time"]
    logger.my_logger.info(
        "{} length: {} minutes, {} seconds.".format(
            name, int(length / 60), int(length % 60)
        )
    )
    for track in mid.tracks[1:]:
        logger.my_logger.debug(track.name)  # print all channel from 0
    return partition, length
