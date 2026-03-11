from pythainlp.tokenize import word_tokenize as th_tokenize
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Level, Question
import random
import re
import json  # 🌟 เพิ่ม import json ตรงนี้
from pythainlp.tokenize import word_tokenize as th_tokenize


# ---------------------------------------------------------------------------
# Utility: split a Japanese sentence into word-level chunks for Level 5
# ---------------------------------------------------------------------------
def _split_jp_chunks(sentence):
    clean = sentence.rstrip('。？！')
    if '|' in clean:
        return [s.strip() for s in clean.split('|') if s.strip()]
    parts = re.split(r'(?<=[はがをにでへとも、])', clean)
    parts = [p for p in parts if p.strip()]
    if len(parts) <= 1:
        parts = [clean[i:i + 3] for i in range(0, len(clean), 3)]
    return [p for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# Per-mode question builders
# ---------------------------------------------------------------------------
def _first_meaning(text):
    """Return only the first Thai meaning (before the first comma)."""
    return text.split(',')[0].strip() if text else text

def _mc_question(q, all_qs):
    # สุ่มรูปแบบ (0 = ถามญี่ปุ่นตอบไทย, 1 = ถามไทยตอบญี่ปุ่น)
    ask_type = random.choice([0, 1]) 
    
    if ask_type == 0:
        answer = _first_meaning(q.th_meaning)
        wrong_pool = [_first_meaning(item.th_meaning) for item in all_qs if _first_meaning(item.th_meaning) != answer]
        question_text = q.jp_text
        question_reading = f"[{q.jp_reading}] แปลว่าอะไร?" if q.jp_reading else "คำนี้แปลว่าอะไร?"
    else:
        answer = q.jp_text
        wrong_pool = [item.jp_text for item in all_qs if item.jp_text != answer]
        question_text = _first_meaning(q.th_meaning)
        question_reading = "แปลเป็นภาษาญี่ปุ่นว่าอะไร?"
        
    seen = set()
    unique_wrongs = []
    for w in wrong_pool:
        if w not in seen:
            seen.add(w)
            unique_wrongs.append(w)
            
    wrongs = random.sample(unique_wrongs, min(3, len(unique_wrongs)))
    choices = [answer] + wrongs
    random.shuffle(choices)
    
    return {
        'mode': 'multiple_choice',
        'jp_text': question_text,       
        'jp_reading': question_reading, 
        'th_meaning': answer, 
        'en_meaning': q.en_meaning or '',
        'jp_sentence': q.jp_sentence,
        'th_sentence': q.th_sentence,
        'choices': choices,             
        'answer': answer,               
        'chunks': [],
    }
    


def _type_answer_question(q):
    """Free-type: user types the Thai meaning from the Japanese word."""
    return {
        'mode': 'type_answer',
        'jp_text': q.jp_text,
        'jp_reading': q.jp_reading,
        'th_meaning': q.th_meaning,
        'en_meaning': q.en_meaning or '',
        'jp_sentence': q.jp_sentence,
        'th_sentence': q.th_sentence,
        'choices': [],
        'answer': q.th_meaning,
        'chunks': [],
    }


def _fill_blank_question(q, all_meanings):
    """
    Fill-in-the-blank: show Thai sentence with last word blanked.
    Choices are Thai meanings (1 correct + 4 distractors).
    """
    th_sent = (q.th_sentence or q.th_meaning or '').strip()

    # Tokenize Thai sentence; blank a random meaningful token (len >= 2)
    tokens = [t for t in th_tokenize(th_sent, engine='newmm') if t.strip()]
    candidates = [i for i, t in enumerate(tokens) if len(t) >= 2]
    if candidates:
        idx        = random.choice(candidates)
        blank_word = tokens[idx]
        th_display = ''.join(tokens[:idx]) + '___' + ''.join(tokens[idx+1:])
    elif tokens:
        blank_word = tokens[-1]
        th_display = ''.join(tokens[:-1]) + '___'
    else:
        blank_word = th_sent
        th_display = '___'

    # Build wrong choices: split every meaning by comma AND space → individual short words
    seen = {blank_word}
    unique_wrongs = []
    for m in all_meanings:
        for part in m.split(','):
            for word in part.strip().split():
                word = word.strip()
                if word and word not in seen and len(word) >= 2:
                    seen.add(word)
                    unique_wrongs.append(word)
    random.shuffle(unique_wrongs)
    wrongs  = unique_wrongs[:4]
    choices = [blank_word] + wrongs
    random.shuffle(choices)

    return {
        'mode': 'fill_blank',
        'jp_text': q.jp_text,
        'jp_reading': q.jp_reading,
        'th_meaning': q.th_meaning,
        'en_meaning': q.en_meaning or '',
        'jp_sentence': q.jp_sentence,
        'th_sentence': th_display,   # Thai sentence with ___
        'choices': choices,
        'answer': blank_word,
        'chunks': [],
    }


def _sort_sentence_question(q, all_meanings):
    """
    Sentence-sort: show JP sentence, user arranges Thai word tiles to form the translation.
    """
    th_sent = (q.th_sentence or q.th_meaning or '').strip()
    correct_chunks = [t for t in th_tokenize(th_sent, engine='newmm') if t.strip()]

    # Thai decoy words from other meanings pool
    seen = set(correct_chunks)
    decoy_pool = []
    for m in all_meanings:
        for part in m.split(','):
            for word in part.strip().split():
                word = word.strip()
                if word and word not in seen and len(word) >= 2:
                    seen.add(word)
                    decoy_pool.append(word)
    random.shuffle(decoy_pool)
    decoys = decoy_pool[:2]

    all_tiles = correct_chunks + decoys
    random.shuffle(all_tiles)
    return {
        'mode': 'sort_sentence',
        'jp_text': q.jp_sentence or q.jp_text,  # full JP sentence shown at top
        'jp_reading': q.jp_reading,
        'th_meaning': q.th_meaning,
        'en_meaning': q.en_meaning or '',
        'jp_sentence': q.jp_sentence,
        'th_sentence': q.th_sentence,
        'choices': all_tiles,       # shuffled Thai word tiles
        'answer': correct_chunks,   # correct Thai word order
        'chunks': all_tiles,
    }


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------
def home(request):
    """Landing page with Vocabulary Bank and Start Testing buttons."""
    return render(request, 'lessons/home.html')

def vocab_bank(request):
    """Single Page Vocabulary Bank (N5-N1 Tabs)"""
    selected_level = request.GET.get('level', 'N5').upper()
    
    if selected_level not in ['N1', 'N2', 'N3', 'N4', 'N5']:
        selected_level = 'N5'
        
    # 🌟 จุดที่แก้: เพิ่ม question_type='word' เข้าไปใน .filter()
    # เพื่อกรองเอาแค่คำศัพท์ ไม่เอาแถวที่เป็นประโยคมาโชว์มั่วซั่ว
    questions = Question.objects.filter(jlpt_level=selected_level, question_type='word').order_by('jp_text')
    # ตัดความหมายภาษาไทยให้เหลือคำแรกก่อนเครื่องหมายจุลภาค (server-side)
    for q in questions:
        q.th_meaning_first = q.th_meaning.split(',')[0].strip() if q.th_meaning else ''    
    return render(request, 'lessons/vocab_bank.html', {
        'questions': questions,
        'current_level': selected_level
    })

# (ลบ def vocab_bank_level ทิ้งไปเลยครับ ไม่ได้ใช้แล้ว!)

def play_home(request):
    """Level-selection screen for the game (shows 5 game levels)."""
    levels = Level.objects.all().order_by('level_number')
    return render(request, 'lessons/play_home.html', {'levels': levels})


def play_level(request, level_id):
    level = get_object_or_404(Level, level_number=level_id)
    word_qs = list(level.questions.filter(question_type='word'))
    sentence_qs = list(level.questions.filter(question_type='sentence'))
    all_qs = word_qs + sentence_qs

    if not all_qs:
        return render(request, 'lessons/play.html', {
            'level': level,
            'questions_json': "[]",
            'level_id': level_id,
            'error': 'ยังไม่มีคำถามในด่านนี้',
        })

    all_meanings = [q.th_meaning for q in word_qs]
    questions_data = []

    if level_id in (1, 2):
        pool_src = word_qs if word_qs else all_qs
        pool = random.sample(pool_src, min(5, len(pool_src)))
        for q in pool:
            questions_data.append(_mc_question(q, pool_src)) 
            
    elif level_id == 3:
        word_pool = random.sample(word_qs, min(3, len(word_qs))) if word_qs else []
        sent_pool = random.sample([q for q in sentence_qs if q.jp_sentence] or sentence_qs, min(2, len(sentence_qs))) if sentence_qs else []
        pool = word_pool + sent_pool
        for idx, q in enumerate(pool):
            if idx < 3:
                questions_data.append(_type_answer_question(q))
            else:
                if q.jp_sentence:
                    questions_data.append(_fill_blank_question(q, all_meanings))
                else:
                    questions_data.append(_mc_question(q, all_qs))

    elif level_id == 4:
        fb_pool_src = [q for q in sentence_qs if q.jp_sentence] or [q for q in all_qs if q.jp_sentence]
        if not fb_pool_src: fb_pool_src = all_qs
        pool = random.sample(fb_pool_src, min(5, len(fb_pool_src)))
        for q in pool: questions_data.append(_fill_blank_question(q, all_meanings))

    elif level_id == 5:
        ss_pool_src = [q for q in sentence_qs if q.jp_sentence and q.th_sentence] or [q for q in all_qs if q.jp_sentence and q.th_sentence]
        if not ss_pool_src: ss_pool_src = all_qs
        pool = random.sample(ss_pool_src, min(5, len(ss_pool_src)))
        for q in pool: questions_data.append(_sort_sentence_question(q, all_meanings))

    # 🌟 แปลงเป็น JSON ของจริงตรงนี้ JS จะได้ไม่งง!
    questions_json = json.dumps(questions_data, ensure_ascii=False)

    return render(request, 'lessons/play.html', {
        'level': level,
        'questions_json': questions_json, 
        'level_id': level_id,
    })