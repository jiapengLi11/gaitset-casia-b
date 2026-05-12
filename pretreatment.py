# -*- coding: utf-8 -*-
import argparse
import os
from multiprocessing import Pool
from multiprocessing import TimeoutError as MP_TimeoutError
from time import sleep
from warnings import warn

import cv2
import numpy as np

START = "START"
FINISH = "FINISH"
WARNING = "WARNING"
FAIL = "FAIL"


def boolean_string(s):
    if s.upper() not in {"FALSE", "TRUE"}:
        raise ValueError("Not a valid boolean string")
    return s.upper() == "TRUE"


parser = argparse.ArgumentParser(description="Pretreat gait silhouettes into aligned 64x64 images.")
parser.add_argument("--input_path", required=True, type=str, help="Root path of the raw dataset.")
parser.add_argument("--output_path", required=True, type=str, help="Root path for processed output.")
parser.add_argument("--log_file", default="./pretreatment.log", type=str, help="Log file path.")
parser.add_argument(
    "--log",
    default=False,
    type=boolean_string,
    help="If TRUE, save all logs. Otherwise only warnings and errors are persisted.",
)
parser.add_argument("--worker_num", default=1, type=int, help="Number of subprocesses for pretreatment.")
opt = parser.parse_args()

INPUT_PATH = opt.input_path
OUTPUT_PATH = opt.output_path
IF_LOG = opt.log
LOG_PATH = opt.log_file
WORKERS = opt.worker_num

T_H = 64
T_W = 64


def log2str(pid, comment, logs):
    str_log = ""
    if isinstance(logs, str):
        logs = [logs]
    for log in logs:
        str_log += "# JOB %d : --%s-- %s\n" % (pid, comment, log)
    return str_log


def log_print(pid, comment, logs):
    str_log = log2str(pid, comment, logs)
    if comment in [WARNING, FAIL] or IF_LOG:
        with open(LOG_PATH, "a", encoding="utf-8") as log_f:
            log_f.write(str_log)
    if comment in [START, FINISH] and pid % 500 != 0:
        return
    print(str_log, end="")


def cut_img(img, seq_info, frame_name, pid):
    if img.sum() <= 10000:
        message = "seq:%s, frame:%s, no data, %d." % ("-".join(seq_info), frame_name, img.sum())
        warn(message)
        log_print(pid, WARNING, message)
        return None

    y = img.sum(axis=1)
    y_top = (y != 0).argmax(axis=0)
    y_btm = (y != 0).cumsum(axis=0).argmax(axis=0)
    img = img[y_top:y_btm + 1, :]

    ratio = img.shape[1] / img.shape[0]
    target_width = int(T_H * ratio)
    img = cv2.resize(img, (target_width, T_H), interpolation=cv2.INTER_CUBIC)

    sum_point = img.sum()
    sum_column = img.sum(axis=0).cumsum()
    x_center = -1
    for i in range(sum_column.size):
        if sum_column[i] > sum_point / 2:
            x_center = i
            break
    if x_center < 0:
        message = "seq:%s, frame:%s, no center." % ("-".join(seq_info), frame_name)
        warn(message)
        log_print(pid, WARNING, message)
        return None

    half_width = int(T_W / 2)
    left = x_center - half_width
    right = x_center + half_width
    if left <= 0 or right >= img.shape[1]:
        left += half_width
        right += half_width
        pad = np.zeros((img.shape[0], half_width))
        img = np.concatenate([pad, img, pad], axis=1)
    img = img[:, left:right]
    return img.astype("uint8")


def cut_pickle(seq_info, pid):
    seq_name = "-".join(seq_info)
    log_print(pid, START, seq_name)
    seq_path = os.path.join(INPUT_PATH, *seq_info)
    out_dir = os.path.join(OUTPUT_PATH, *seq_info)
    frame_list = sorted(os.listdir(seq_path))
    count_frame = 0
    for frame_name in frame_list:
        frame_path = os.path.join(seq_path, frame_name)
        raw = cv2.imread(frame_path)
        if raw is None:
            log_print(pid, WARNING, f"seq:{seq_name}, frame:{frame_name}, failed to read image.")
            continue
        img = cut_img(raw[:, :, 0], seq_info, frame_name, pid)
        if img is not None:
            save_path = os.path.join(out_dir, frame_name)
            cv2.imwrite(save_path, img)
            count_frame += 1

    if count_frame < 5:
        message = "seq:%s, less than 5 valid data." % ("-".join(seq_info))
        warn(message)
        log_print(pid, WARNING, message)

    log_print(pid, FINISH, "Contain %d valid frames. Saved to %s." % (count_frame, out_dir))


if __name__ == "__main__":
    if not os.path.isdir(INPUT_PATH):
        raise FileNotFoundError(f"Input path does not exist: {INPUT_PATH}")
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    pool = Pool(WORKERS)
    results = []
    pid = 0

    print(
        "Pretreatment Start.\n"
        "Input path: %s\n"
        "Output path: %s\n"
        "Log file: %s\n"
        "Worker num: %d" % (INPUT_PATH, OUTPUT_PATH, LOG_PATH, WORKERS)
    )

    id_list = sorted(os.listdir(INPUT_PATH))
    for _id in id_list:
        seq_types = sorted(os.listdir(os.path.join(INPUT_PATH, _id)))
        for seq_type in seq_types:
            views = sorted(os.listdir(os.path.join(INPUT_PATH, _id, seq_type)))
            for view in views:
                seq_info = [_id, seq_type, view]
                out_dir = os.path.join(OUTPUT_PATH, *seq_info)
                os.makedirs(out_dir, exist_ok=True)
                results.append(pool.apply_async(cut_pickle, args=(seq_info, pid)))
                sleep(0.02)
                pid += 1

    pool.close()
    unfinished = 1
    while unfinished > 0:
        unfinished = 0
        for i, res in enumerate(results):
            try:
                res.get(timeout=0.1)
            except Exception as e:
                if isinstance(e, MP_TimeoutError):
                    unfinished += 1
                    continue
                print("\n\n\nERROR OCCUR: PID ##%d##, ERRORTYPE: %s\n\n\n" % (i, type(e)))
                raise e
    pool.join()
