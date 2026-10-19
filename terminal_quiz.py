"""No-dependency CLI fallback: `python terminal_quiz.py`.
The full learning experience is available in the Streamlit browser app.
"""
import textwrap
import quiz_core as core


def ask(prompt, default=''):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print('\nSee you next time. Your quiz history is saved.')
        raise SystemExit(0)


def display(question, profile, sid):
    print('\n'+'─'*70)
    print(textwrap.fill(question['prompt'],width=72))
    print(f'[{question["difficulty"]} · {question["topic_name"]} · {question["source"]}]')
    if question.get('code'):
        print('\n'+question['code'])
    for n,opt in enumerate(question['options']):
        print(f'  {"ABCD"[n]}. {opt}')
    past=core.get_answer(profile,sid,question['id'])
    if past is None:
        while True:
            val=ask('\nYour answer [A/B/C/D, S = save & quit]: ').upper()
            if val=='S':return False
            if val in 'ABCD' and len(val)==1:break
            print('Choose A, B, C, D or S.')
        core.save_answer(profile,sid,question,'ABCD'.index(val))
        past=core.get_answer(profile,sid,question['id'])
    if past['correct']:
        print('\n✅ Correct!')
    else:
        print(f'\n❌ Not quite. You chose {"ABCD"[past["answer_index"]]}.')
    right=question['answer']
    print(f'✅ Correct answer: {"ABCD"[right]}. {question["options"][right]}')
    print('WHY: '+textwrap.fill(question['explanation'],width=70))
    ask('Press Enter to continue... ')
    return True


def run_session(profile,lookup,sid):
    while True:
        session=core.get_session(profile,sid)
        pos=session['position']
        if pos>=len(session['queue']):
            print('\n🎉 Session complete! Progress is saved.')
            return
        q=lookup.get(session['queue'][pos])
        if not q:
            print('This question is missing. Restore its pack to resume.')
            return
        print(f'\nQUESTION {pos+1} OF {len(session["queue"])}')
        if not display(q,profile,sid):
            print('Session saved. You can resume it later.')
            return
        core.change_position(profile,sid,pos+1)


def main():
    core.init_db()
    packs=core.load_packs()
    bank=[q for p in packs.values() for q in p['questions']]
    lookup={q['id']:q for q in bank}
    print('\n🐍 PYTHON MASTERY LAB • Terminal Edition')
    print('The full dashboard, coding dojo and pack import are in app.py (Streamlit).')
    profile=ask('Your learner name [My Python practice]: ') or 'My Python practice'
    while True:
        stats=core.profile_metrics(profile)
        print(f'\n{len(bank)} MCQs | {stats["attempts"]} answered | {stats["missed"]} missed | {stats["due"]} due')
        print('1) New mixed quiz   2) Missed questions   3) Due review')
        print('4) Resume session   5) Unseen only        6) Quit')
        choice=ask('Choose 1–6: ')
        if choice=='6':return
        if choice=='4':
            sessions=core.recent_sessions(profile,limit=20,unfinished=True)
            if not sessions:
                print('No unfinished sessions.');continue
            for idx,s in enumerate(sessions,1):
                print(f'  {idx}. {s["created_at"][:16]} — {s["position"]}/{len(s["queue"])} answered')
            text=ask('Resume which session number? ')
            if not text.isdigit() or not 1<=int(text)<=len(sessions):continue
            run_session(profile,lookup,sessions[int(text)-1]['id'])
            continue
        mode={'1':'Smart Mix','2':'Missed','3':'Due','5':'Unseen'}.get(choice)
        if mode is None:
            print('Choose 1, 2, 3, 4, 5 or 6.');continue
        raw=ask('How many questions? [10]: ') or '10'
        if not raw.isdigit() or int(raw)<1:
            print('Enter a positive integer.');continue
        queue=core.select_questions(bank,profile,min(int(raw),len(bank)),mode)
        if not queue:
            print('No matching questions. Try mixed mode.');continue
        sid=core.new_session(profile,'mcq',queue,{'mode':mode})
        run_session(profile,lookup,sid)


if __name__=='__main__':main()
