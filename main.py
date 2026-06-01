import os
import json
import time

from json_repair import loads

import multiprocessing as mp
from functools import partial

from llm_api import LLMChat
from tools import get_subtitle_content, get_subtitle_content_with_format, create_srt_from_dict, printc
from prompts import text_split_prompt, translate_one_slice_prompt

DEBUG = False
RECORD = True
RETRY_TIME = 2
MP_NUM = 3

if DEBUG:
    RECORD = False

config = {
    'min_per_num': 50,
    'max_per_num': 150,
    'max_thres': 200
}

model = LLMChat('kimi')

def _check_slice_valid(slices, last_index):
    num = len(slices)
    assert slices[0][0] == 1
    assert slices[num - 1][1] == last_index
    assert slices[0][1] > slices[0][0]
    print('第1节包含字幕条数：{}'.format(slices[0][1] - slices[0][0] + 1))

    for i in range(1, num):
        assert slices[i][1] > slices[i][0]
        assert slices[i][0] == slices[i - 1][1] + 1
        print('第{}节包含字幕条数：{}'.format(i + 1, slices[i][1] - slices[i][0] + 1))

def subtitle_split(file_path, video_introduction_prompt):

    text_all, texts, durations = get_subtitle_content(file_path)

    prompt_ = text_split_prompt.format(
        min_per_num = config['min_per_num'],
        max_per_num = config['max_per_num'],
        max_thres = config['max_thres'],
        text_all = text_all,
        video_introduction_prompt = video_introduction_prompt
    )

    if RECORD:
        with open('logs/prompt-split.txt', 'w', encoding='utf-8') as f:
            f.write(prompt_)

    if DEBUG:
        with open('logs/output-split.txt', 'r', encoding='utf-8') as f:
            result = f.read()
        result = loads(result)
    else:
        for i in range(RETRY_TIME):
            try:
                result = model.get_response(prompt_, backoff=True, thinking=True)['answer']

                if RECORD:
                    with open('logs/output-split.txt', 'w', encoding='utf-8') as f:
                        f.write(result)

                result = loads(result)
                break
            except Exception as e:
                print('text split err: {}\ntry time: {}'.format(e, i + 1))
                if i == RETRY_TIME - 1:
                    raise RuntimeError('text split error')

    content_total = result['content']
    result = result['split']
    slices = []
    for i in range(len(result)):
        slices.append([result[i]['start'], result[i]['end'], result[i]['content']])

    slices = sorted(slices, key = lambda x: x[0])

    _check_slice_valid(slices, last_index = len(texts))

    return content_total, slices







def translate_subtitle_one_slice(slice, file_path, content_total, source_language, video_introduction_prompt):
    text_all, duration_all = get_subtitle_content_with_format(file_path, slice[0], slice[1])

    prompt_ = translate_one_slice_prompt.format(
        source_language = source_language,
        video_introduction_prompt = video_introduction_prompt,
        content_total = content_total,
        content_slice = slice[2],
        text = json.dumps(text_all)
    )

    if RECORD:
        with open('logs/prompt-translate{}_{}.txt'.format(slice[0],slice[1]), 'w', encoding='utf-8') as f:
            f.write(prompt_)

    if DEBUG:
        with open('logs/output-translate{}_{}.txt'.format(slice[0],slice[1]), 'r', encoding='utf-8') as f:
            result = f.read()
        result = loads(result)
    else:
        for i in range(RETRY_TIME):
            try:
                result = model.get_response(prompt_, backoff=True, thinking=True)['answer']

                if RECORD:
                    with open('logs/output-translate{}_{}.txt'.format(slice[0],slice[1]), 'w', encoding='utf-8') as f:
                        f.write(result)

                result = loads(result)
                break
            except Exception as e:
                print('translate {}-{} err: {}\ntry time: {}'.format(slice[0], slice[1], e, i + 1))
                if i == RETRY_TIME - 1:
                    raise RuntimeError('translate {}-{} err'.format(slice[0], slice[1]))

    for key in result:
        if key in duration_all:
            duration_all[key]['text'] = result[key]
        else:
            printc('WARNING: {} in result not in duration'.format(key), 'yellow')
    return duration_all



def translate_subtitle_mp(file_path, save_path, source_language, video_introduction = None):

    if video_introduction is None:
        video_introduction_prompt = ''
    else:
        video_introduction_prompt = '\n视频内容介绍：\n{}\n'.format(video_introduction)

    content_total, slices = subtitle_split(file_path, video_introduction_prompt)

    subs_all = dict()
    func = partial(translate_subtitle_one_slice, 
                   file_path = file_path, 
                   content_total = content_total, 
                   source_language = source_language, 
                   video_introduction_prompt = video_introduction_prompt)

    with mp.Pool(processes = MP_NUM) as pool:
        results = pool.map(func, slices)

    for result in results:
        subs_all.update(result)
    
    create_srt_from_dict(file_path, subs_all, save_path)


if __name__ == "__main__":
    source_language = "英语"
    file_path = "2.srt"
    save_path = "2_chinese.srt"
    video_introduction = ''

    try:
        btime = time.time()
        translate_subtitle_mp(file_path, save_path, source_language, video_introduction)
        etime = time.time()
        print('用时：{}秒'.format(etime - btime))
    except:
        raise
    finally:
        print(model.get_price())
