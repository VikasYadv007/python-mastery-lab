"""Reference examples must run and match all provided expected outputs."""
import contextlib
import io
import json
from pathlib import Path

PACK = json.loads((Path(__file__).resolve().parents[1]/'packs'/'lecture_1.json').read_text(encoding='utf8'))


def test_all_coding_examples():
    count=0
    for problem in PACK['challenges']:
        for sample in problem['samples']:
            lines=iter([] if sample['input']=='(none)' else sample['input'].split('\n'))
            def mock_input(prompt=''):
                return next(lines)
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(compile(problem['solution'],problem['id'],'exec'),{'input':mock_input,'__name__':'__main__'})
            assert output.getvalue().strip()==sample['output'].strip(),(problem['id'],sample)
            count+=1
    assert count==57


def test_famous_output_traps():
    ids=('L1-M062','L1-M063','L1-M113','L1-M116','L1-M117','L1-M118','L1-M122',
         'L1-M123','L1-M124','L1-M126','L1-M127','L1-M128','L1-M130','L1-M135','L1-M177')
    lookup={q['id']:q for q in PACK['questions']}
    for key in ids:
        item=lookup[key]
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(item['code'],key,'exec'),{})
        assert output.getvalue().strip()==item['options'][item['answer']],key
