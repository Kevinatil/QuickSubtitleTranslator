import os
import re
import pysrt

from .utils import printc

def subtitle_regular(subs):
    changed = False
    for i, sub in enumerate(subs):
        if sub.index != i + 1:
            sub.index = i + 1
            changed = True
    if changed:
        printc('WARNING: index was changed', 'yellow')
    return subs

def text_regular(text):
    text = re.sub(r'[。，、]', ' ', text)
    text = re.sub(r'【', '[', text)
    text = re.sub(r'】', ']', text)
    return text

def get_subtitle_content(file_path):
    texts = []
    durations = []
    subs = pysrt.open(file_path)
    subs = subtitle_regular(subs)
    text_all = ''

    for i in range(len(subs)):
        text_ = subs[i].text
        if text_.find('<B>') >= 0 or text_.find('<E>') >= 0:
            printc('WARNING: line {} has <B/E>, {}'.format(subs[i].index, text_), 'yellow')
        text_ = '{}<B>{}<E>'.format(subs[i].index, text_)
        text_all += text_ + '\n'
        texts.append(text_)
        durations.append((subs[i].start, subs[i].end))

    return text_all, texts, durations

def get_subtitle_content_with_format(file_path, begin_index, end_index):
    subs = pysrt.open(file_path)
    subs = subtitle_regular(subs)
    text_all = dict()
    duration_all = dict()

    for i in range(len(subs)):
        idx_ = subs[i].index
        if idx_ >= begin_index and idx_ <= end_index:
            text_all[str(idx_)] = subs[i].text
            duration_all[str(idx_)] = {
                'duration': (subs[i].start, subs[i].end)
            }
        if idx_ > end_index:
            break
    assert len(text_all) == end_index - begin_index + 1
    return text_all, duration_all

def create_srt_from_dict(file_path, subs_dict, save_path):
    subs_origin = pysrt.open(file_path)
    subs_origin = subtitle_regular(subs_origin)

    num = len(subs_origin)

    subs = pysrt.SubRipFile()
    for i in range(1, num + 1):
        idx = str(i)
        subtitle = pysrt.SubRipItem()

        if idx not in subs_dict:
            printc('WARNING: index {} not in subs_dict'.format(i), 'yellow')
            
            subtitle.index = subs_origin[i - 1].index
            subtitle.start = subs_origin[i - 1].start
            subtitle.end = subs_origin[i - 1].end
            subtitle.text = subs_origin[i - 1].text
            subs.append(subtitle)
        else:
            subtitle.index = idx
            subtitle.start = subs_dict[idx]['duration'][0]
            subtitle.end = subs_dict[idx]['duration'][1]
            subtitle.text = text_regular(subs_dict[idx]['text'])
            subs.append(subtitle)
    
    subs.save(save_path, encoding='utf-8')
