LOG_ORIGIN = "log_from"
LOG_STEP_LABEL = "step_label"
LOG_RECORD_ID = "record_id"
LOG_STEP_STATUS = "step_status"


class StepStatus:

    INIT = 0
    DATA_READY = 10
    PROCESSING = 20
    DONE = 30
    ERROR = 40
    DATA_NOT_AVIABLE = 41


def record_log_file_path(data_path, rec_id):
    return data_path / "LOG" / "{}.log".format(rec_id)
