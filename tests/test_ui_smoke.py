"""Offline smoke checks for Streamlit page paths, without installing Streamlit.

This validates the Python/UI paths, NOT browser rendering. Browser appearance must
still be checked in a real Streamlit installation.
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path


class RerunSignal(Exception):
    pass


class FakeStreamlit:
    def __init__(self, page='home', dark=False, pressed=()):
        self.session_state = {'current_page': page, 'dark_mode': dark}
        self.query_params = {'theme': 'dark' if dark else 'light'}
        self.sidebar = self
        self.pressed = set(pressed)
        self.markups = []
        self.warnings = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def set_page_config(self, **kwargs):
        pass

    def markdown(self, text, **kwargs):
        self.markups.append(text)

    def button(self, label, **kwargs):
        # Buttons in different panels share labels but have distinct keys.
        return kwargs.get('key', label) in self.pressed

    def form_submit_button(self, label, **kwargs):
        return label in self.pressed

    def text_input(self, label, **kwargs):
        return kwargs.get('value', '')

    def text_area(self, label, **kwargs):
        return kwargs.get('value', '')

    def selectbox(self, label, options, **kwargs):
        return list(options)[0]

    def multiselect(self, label, options, **kwargs):
        return kwargs.get('default', [])

    def number_input(self, label, **kwargs):
        return kwargs.get('value', 1)

    def radio(self, label, options, **kwargs):
        return list(options)[0]

    def columns(self, spec, **kwargs):
        return [self] * (spec if isinstance(spec,int) else len(spec))

    def tabs(self, spec, **kwargs):
        return [self] * len(spec)

    def popover(self, label, **kwargs):
        return self

    def container(self, **kwargs):
        return self

    def form(self, *args, **kwargs):
        return self

    def expander(self, *args, **kwargs):
        return self

    def toggle(self, label, **kwargs):
        return self.session_state.get(kwargs.get('key', ''), False)

    def rerun(self):
        raise RerunSignal()

    def stop(self):
        raise RuntimeError('App stopped unexpectedly')

    def file_uploader(self, *args, **kwargs):
        return None

    def __getattr__(self, name):
        if name in ('session_state','query_params','sidebar'):
            raise AttributeError(name)
        def noop(*args,**kwargs):
            if name=='warning':
                self.warnings.append(args[0] if args else '')
        return noop


def run_app(tmp, *, page='home', dark=False, pressed=(), active=None):
    fake=FakeStreamlit(page,dark,pressed)
    if active:
        fake.session_state['active_session_id']=active
    sys.modules['streamlit']=fake
    spec=importlib.util.spec_from_file_location('smoke_app',tmp/'app.py')
    mod=importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except RerunSignal:
        pass
    return mod,fake


def test_app_paths_and_theme(tmp_path, monkeypatch):
    origin=Path(__file__).resolve().parents[1]
    # Copy the app and bank so the test can never mutate the user's progress DB.
    for file in ('app.py','quiz_core.py','ui_style.py'):
        shutil.copy2(origin/file,tmp_path/file)
    shutil.copytree(origin/'packs',tmp_path/'packs')
    monkeypatch.syspath_prepend(str(tmp_path))
    # Only fake the visual framework. Real quiz_core+SQLite are exercised.
    import quiz_core as core
    assert len(core.load_packs()) >= 1
    try:
        for page in ('home','quiz','coding','review','progress','packs'):
            for dark in (False,True):
                app,st=run_app(tmp_path,page=page,dark=dark)
                assert st.session_state['current_page']==page
                assert any('<style>' in x and 'stSidebarCollapsedControl' in x for x in st.markups)
                css='\n'.join(x for x in st.markups if '<style>' in x)
                assert 'data:image/svg+xml' in css
                if dark:
                    assert '--bg:#0c1221;' in css
                else:
                    assert '--bg:#f6f8fd;' in css
                assert 'visibility:hidden' not in css.split('footer')[0]
        # Known UTC timestamp, including a date boundary crossing in IST.
        assert app.as_ist('2026-10-18T13:00:00+00:00')=='18 Oct 2026, 06:30 PM IST'
        assert app.as_ist('2026-10-18T22:00:00Z')=='19 Oct 2026, 03:30 AM IST'
        assert app.as_ist('2026-10-18T13:00:00')=='18 Oct 2026, 06:30 PM IST'
        assert app.as_ist(None)=='—'

        pack=next(iter(core.load_packs().values()))
        q=pack['questions'][0]
        # Test saved-session question view, revealed explanation view and finish screen.
        sid=core.new_session('My Python practice','mcq',[q['id']])
        run_app(tmp_path,page='quiz',active=sid)
        _,st=run_app(tmp_path,page='quiz',active=sid,pressed=('Check my answer',))
        ans=core.get_answer('My Python practice',sid,q['id'])
        assert ans is not None
        assert ans['answer_index']==0
        app,st=run_app(tmp_path,page='quiz',active=sid)
        assert any('Explanation' in x or 'Why:' in x for x in st.markups)
        core.change_position('My Python practice',sid,1)
        run_app(tmp_path,page='quiz',active=sid)
        # Profile metrics and CSV export carry IST while keeping raw UTC dates.
        run_app(tmp_path,page='progress')
        exported=app.attempts_export_ist('My Python practice').decode('utf-8-sig')
        assert 'saved_at_ist' in exported and 'IST' in exported and 'created_at' in exported
        backup=app.consistent_db_backup()
        assert backup[:16] == b'SQLite format 3\x00'
        # Sidebar navigation is complemented with a menu reachable when collapsed.
        _,st=run_app(tmp_path,page='home',pressed=('top_nav_review',))
        assert st.session_state['current_page']=='review'
        assert st.query_params['page']=='review'
    finally:
        sys.modules.pop('streamlit',None)
        sys.modules.pop('quiz_core',None)
        sys.modules.pop('ui_style',None)
