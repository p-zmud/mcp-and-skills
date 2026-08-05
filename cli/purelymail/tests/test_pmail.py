"""pmail tests - offline: urllib, imaplib and smtplib are replaced with fakes.

Run:  pytest cli/purelymail/tests/
"""
import importlib.util
import io
import json
import os
import sys

import pytest

_PMAIL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "pmail")
_spec = importlib.util.spec_from_loader("pmail", importlib.machinery.SourceFileLoader("pmail",
                                                                                     _PMAIL))
pmail = importlib.util.module_from_spec(_spec)
sys.modules["pmail"] = pmail
_spec.loader.exec_module(pmail)


# ---------------------------------------------------------------- fixtures / fakes

@pytest.fixture(autouse=True)
def config(tmp_path, monkeypatch):
    """Every test gets its own config - the real ~/.config/pmail is never touched."""
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "api_token": "tok-test",
        "default_mailbox": "you@example.com",
        "mailboxes": {"you@example.com": "app-pass", "second@example.com": "app-pass-2"},
    }), encoding="utf-8")
    monkeypatch.setenv("PMAIL_CONFIG", str(path))
    return path


def run(argv, capsys):
    pmail.main(argv)
    return capsys.readouterr()


def run_json(argv, capsys):
    return json.loads(run(argv, capsys).out)


class FakeHTTPResponse(io.BytesIO):
    def __init__(self, payload):
        io.BytesIO.__init__(self, json.dumps(payload).encode("utf-8"))


class FakeAPI:
    """Stand-in for urllib.request.urlopen - records calls and returns canned responses."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, req, timeout=None):
        op = req.full_url.rsplit("/", 1)[-1]
        self.calls.append((op, json.loads(req.data.decode("utf-8")),
                           dict(req.header_items())))
        if op not in self.responses:
            raise AssertionError("unexpected API call: %s" % op)
        payload = self.responses[op]
        return FakeHTTPResponse(payload.pop(0) if isinstance(payload, list) else payload)


@pytest.fixture
def api(monkeypatch):
    def install(responses):
        fake = FakeAPI(responses)
        monkeypatch.setattr(pmail.urllib.request, "urlopen", fake)
        return fake
    return install


HEADERS = (b"From: =?UTF-8?B?Sm9zw6kgw4FsdmFyZXo=?= <jose@example.com>\r\n"
           b"To: you@example.com\r\n"
           b"Subject: =?UTF-8?B?w5xiZXJmw6RsbGlnZSBSZWNobnVuZw==?=\r\n"
           b"Date: Tue, 5 Aug 2026 09:00:00 +0200\r\n\r\n")

FULL_MAIL = (b"From: Jose <jose@example.com>\r\n"
             b"To: you@example.com\r\n"
             b"Cc: office@example.com\r\n"
             b"Subject: Test\r\n"
             b"Message-ID: <orig-123@example.com>\r\n"
             b"References: <older-1@example.com>\r\n"
             b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
             b"Caf\xc3\xa9 message body.\r\n")


class FakeIMAP:
    instances = []
    fetch_override = None    # tests drop their own UID FETCH response in here

    def __init__(self, host, port, ssl_context=None):
        self.host = host
        self.port = port
        self.commands = []
        self.selected = None
        self.literal = None
        self.logged_out = False
        self.appended = []
        self.search_result = [b"1 2 3"]
        self.fetch_result = (FakeIMAP.fetch_override
                             or [(b"1 (UID 3 FLAGS (\\Seen))", HEADERS), b")"])
        FakeIMAP.instances.append(self)

    def login(self, user, password):
        self.user, self.password = user, password
        return ("OK", [b"Logged in"])

    def select(self, folder, readonly=False):
        self.selected = (folder, readonly)
        return ("OK", [b"3"])

    def list(self):
        return ("OK", [b'(\\Sent) "." "Sent"', b'() "." "INBOX"'])

    def uid(self, command, *args):
        self.commands.append((command, args, self.literal))
        self.literal = None
        if command == "SEARCH":
            return ("OK", self.search_result)
        if command == "FETCH":
            return ("OK", self.fetch_result)
        return ("OK", [b"done"])

    def append(self, folder, flags, date, message):
        self.appended.append((folder, flags, message))
        return ("OK", [b"APPEND completed"])

    def expunge(self):
        self.commands.append(("EXPUNGE", (), None))
        return ("OK", [b"1"])

    def logout(self):
        self.logged_out = True
        return ("BYE", [b"bye"])


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=None, context=None):
        self.host, self.port = host, port
        self.sent = []
        FakeSMTP.instances.append(self)

    def login(self, user, password):
        self.user, self.password = user, password

    def send_message(self, msg):
        self.sent.append(msg)

    def quit(self):
        self.quit_called = True


@pytest.fixture(autouse=True)
def fake_mail(monkeypatch):
    FakeIMAP.instances = []
    FakeIMAP.fetch_override = None
    FakeSMTP.instances = []
    monkeypatch.setattr(pmail.imaplib, "IMAP4_SSL", FakeIMAP)
    monkeypatch.setattr(pmail.smtplib, "SMTP_SSL", FakeSMTP)


# ---------------------------------------------------------------- API v0

def test_credit_sends_the_token_in_the_header(api, capsys):
    fake = api({"checkAccountCredit": {"type": "success", "result": {"credit": "0.36"}}})
    assert run_json(["credit"], capsys) == {"credit": "0.36"}
    op, body, headers = fake.calls[0]
    assert op == "checkAccountCredit" and body == {}
    assert headers["Purelymail-api-token"] == "tok-test"


def test_api_error_exits_with_2(api, capsys):
    api({"listUser": {"type": "error", "code": "invalidToken", "message": "Token not valid."}})
    with pytest.raises(SystemExit) as e:
        pmail.main(["users"])
    assert e.value.code == 2
    assert "Token not valid" in capsys.readouterr().err


def test_domains_passes_include_shared(api, capsys):
    fake = api({"listDomains": {"type": "success", "result": {"domains": []}}})
    run_json(["domains", "--shared"], capsys)
    assert fake.calls[0][1] == {"includeShared": True}


def test_alias_add_builds_the_rule(api, capsys):
    fake = api({"createRoutingRule": {"type": "success", "result": {}}})
    run_json(["alias", "add", "--domain", "example.com", "--match", "shop",
              "--target", "you@example.com", "--prefix"], capsys)
    assert fake.calls[0][1] == {"domainName": "example.com", "matchUser": "shop",
                                "targetAddresses": ["you@example.com"],
                                "prefix": True, "catchall": False}


def test_alias_list_filters_by_domain(api, capsys):
    api({"listRoutingRules": {"type": "success", "result": {"rules": [
        {"id": 1, "domainName": "example.com"}, {"id": 2, "domainName": "other.example"}]}}})
    res = run_json(["alias", "list", "--domain", "EXAMPLE.COM"], capsys)
    assert res["count"] == 1 and res["rules"][0]["id"] == 1


def test_alias_rm_without_yes_calls_no_api(api, capsys):
    fake = api({})
    with pytest.raises(SystemExit) as e:
        pmail.main(["alias", "rm", "--id", "7"])
    assert e.value.code == 2 and fake.calls == []


def test_user_rm_without_yes_calls_no_api(api, capsys):
    fake = api({})
    with pytest.raises(SystemExit):
        pmail.main(["user", "rm", "you@example.com"])
    assert fake.calls == []


def test_user_rm_with_yes_cleans_the_config(api, capsys, config):
    api({"deleteUser": {"type": "success", "result": {}}})
    run_json(["user", "rm", "second@example.com", "--yes"], capsys)
    saved = json.loads(config.read_text(encoding="utf-8"))
    assert "second@example.com" not in saved["mailboxes"]
    assert saved["default_mailbox"] == "you@example.com"


def test_domain_rm_counts_the_mailboxes_it_would_delete(api, capsys):
    api({"listUser": {"type": "success", "result": {
        "users": ["you@example.com", "second@example.com", "x@other.example"]}}})
    with pytest.raises(SystemExit):
        pmail.main(["domain", "rm", "example.com"])
    err = capsys.readouterr().err
    assert "2 mailboxes" in err and "second@example.com" in err


def test_user_create_splits_the_address(api, capsys):
    fake = api({"createUser": {"type": "success", "result": {}}})
    run_json(["user", "create", "new@example.com", "--password", "secret"], capsys)
    body = fake.calls[0][1]
    assert body["userName"] == "new" and body["domainName"] == "example.com"
    assert body["sendWelcomeEmail"] is False


def test_setup_generates_passwords_and_is_idempotent(api, capsys, config):
    fake = api({
        "listUser": {"type": "success", "result": {
            "users": ["you@example.com", "second@example.com", "fresh@example.com"]}},
        "createAppPassword": {"type": "success", "result": {"appPassword": "freshly-generated"}},
    })
    res = run_json(["setup", "--token", "tok-new"], capsys)
    assert res["app_passwords_created"] == ["fresh@example.com"]
    assert sorted(res["already_configured"]) == ["second@example.com", "you@example.com"]
    saved = json.loads(config.read_text(encoding="utf-8"))
    assert saved["mailboxes"]["you@example.com"] == "app-pass"        # not overwritten
    assert saved["mailboxes"]["fresh@example.com"] == "freshly-generated"
    assert saved["api_token"] == "tok-new"
    assert [c[0] for c in fake.calls].count("createAppPassword") == 1


def test_setup_writes_the_config_with_mode_600(api, capsys, tmp_path, monkeypatch):
    monkeypatch.setenv("PMAIL_CONFIG", str(tmp_path / "new" / "config.json"))
    api({"listUser": {"type": "success", "result": {"users": ["a@example.com"]}},
         "createAppPassword": {"type": "success", "result": {"appPassword": "pw"}}})
    res = run_json(["setup", "--token", "tok"], capsys)
    assert res["default_mailbox"] == "a@example.com"
    assert oct(os.stat(tmp_path / "new" / "config.json").st_mode)[-3:] == "600"


def test_setup_default_for_an_unknown_mailbox_fails(capsys):
    with pytest.raises(SystemExit) as e:
        pmail.main(["setup", "--default", "stranger@example.com"])
    assert e.value.code == 2


# ---------------------------------------------------------------- IMAP / SMTP

def test_inbox_returns_decoded_headers(capsys):
    res = run_json(["inbox", "-n", "5"], capsys)
    M = FakeIMAP.instances[0]
    assert (M.host, M.port) == (pmail.IMAP_HOST, pmail.IMAP_PORT)
    assert M.user == "you@example.com" and M.password == "app-pass"
    assert M.selected == ('"INBOX"', True)
    assert res["messages"][0]["subject"] == "Überfällige Rechnung"
    assert res["messages"][0]["from"] == "José Álvarez <jose@example.com>"
    assert res["messages"][0]["unread"] is False
    assert M.logged_out


def test_inbox_unread_uses_the_UNSEEN_criterion(capsys):
    run_json(["inbox", "--unread"], capsys)
    search = [c for c in FakeIMAP.instances[0].commands if c[0] == "SEARCH"][0]
    assert search[1] == (None, "UNSEEN")


def test_inbox_takes_the_last_n_newest_first(capsys, monkeypatch):
    monkeypatch.setattr(pmail, "fetch_headers", lambda M, uids: [{"uid": u} for u in uids])
    res = run_json(["inbox", "-n", "2"], capsys)
    assert [m["uid"] for m in res["messages"]] == [3, 2]


def test_mailbox_flag_picks_another_mailbox(capsys):
    run_json(["--mailbox", "second@example.com", "inbox"], capsys)
    assert FakeIMAP.instances[0].user == "second@example.com"


def test_unknown_mailbox_fails(capsys):
    with pytest.raises(SystemExit) as e:
        pmail.main(["--mailbox", "stranger@example.com", "inbox"])
    assert e.value.code == 2
    assert "has no app password" in capsys.readouterr().err


def test_ascii_search_goes_without_a_literal(capsys):
    run_json(["search", "invoice", "--from", "jose@example.com", "--since", "2026-08-01"],
             capsys)
    cmd, args, literal = [c for c in FakeIMAP.instances[0].commands if c[0] == "SEARCH"][0]
    assert args == (None, "FROM", '"jose@example.com"', "SINCE", "01-Aug-2026",
                    "TEXT", '"invoice"')
    assert literal is None


def test_non_ascii_search_uses_a_utf8_literal(capsys):
    run_json(["search", "café"], capsys)
    cmd, args, literal = [c for c in FakeIMAP.instances[0].commands if c[0] == "SEARCH"][0]
    assert args == ("CHARSET", "UTF-8", "TEXT")
    assert literal == "café".encode("utf-8")


def test_search_with_a_bad_date_fails(capsys):
    with pytest.raises(SystemExit) as e:
        pmail.main(["search", "x", "--since", "05.08.2026"])
    assert e.value.code == 2


def test_read_prints_human_readable_text(capsys):
    FakeIMAP.fetch_override = [(b"1 (UID 9 FLAGS (\\Seen))", FULL_MAIL), b")"]
    res = run(["read", "9"], capsys)
    assert "Subject: Test" in res.out
    assert "Café message body." in res.out
    assert "jose@example.com" in res.out


def test_read_json_returns_a_structure(capsys, monkeypatch):
    monkeypatch.setattr(pmail, "fetch_message", lambda M, uid: (
        pmail.email.message_from_bytes(FULL_MAIL), ["\\Seen"]))
    res = run_json(["read", "9", "--json"], capsys)
    assert res["message_id"] == "<orig-123@example.com>"
    assert res["body"] == "Café message body."
    assert res["attachments"] == []


def test_send_sends_and_appends_to_sent(capsys):
    res = run_json(["send", "--to", "someone@example.com", "--subject", "Grüße",
                    "--body", "Grüße aus Köln"], capsys)
    S = FakeSMTP.instances[0]
    assert (S.host, S.port) == (pmail.SMTP_HOST, pmail.SMTP_PORT)
    msg = S.sent[0]
    assert msg["To"] == "someone@example.com"
    assert msg["From"] == "you@example.com"
    assert msg.get_content().strip() == "Grüße aus Köln"
    appended = FakeIMAP.instances[-1].appended[0]
    assert appended[0] == '"Sent"' and appended[1] == r"\Seen"
    assert res["appended_to"] == "Sent"


def test_send_without_a_body_fails(capsys):
    with pytest.raises(SystemExit) as e:
        pmail.main(["send", "--to", "someone@example.com", "--subject", "x"])
    assert e.value.code == 2
    assert FakeSMTP.instances == []


def test_send_with_an_attachment(capsys, tmp_path):
    f = tmp_path / "report.txt"
    f.write_text("data", encoding="utf-8")
    run_json(["send", "--to", "someone@example.com", "--subject", "x", "--body", "y",
              "--attach", str(f)], capsys)
    names = [p.get_filename() for p in FakeSMTP.instances[0].sent[0].walk()]
    assert "report.txt" in names


def test_reply_sets_in_reply_to_and_references(capsys, monkeypatch):
    monkeypatch.setattr(pmail, "fetch_message", lambda M, uid: (
        pmail.email.message_from_bytes(FULL_MAIL), ["\\Seen"]))
    res = run_json(["reply", "9", "--body", "ok"], capsys)
    msg = FakeSMTP.instances[0].sent[0]
    assert msg["In-Reply-To"] == "<orig-123@example.com>"
    assert msg["References"] == "<older-1@example.com> <orig-123@example.com>"
    assert msg["Subject"] == "Re: Test"
    assert res["to"] == ["jose@example.com"] and res["cc"] == []


def test_reply_all_adds_cc_without_your_own_address(capsys, monkeypatch):
    monkeypatch.setattr(pmail, "fetch_message", lambda M, uid: (
        pmail.email.message_from_bytes(FULL_MAIL), ["\\Seen"]))
    res = run_json(["reply", "9", "--body", "ok", "--all"], capsys)
    assert res["cc"] == ["office@example.com"]


def test_mark_read_sets_the_flag(capsys):
    res = run_json(["mark", "5", "read"], capsys)
    store = [c for c in FakeIMAP.instances[0].commands if c[0] == "STORE"][0]
    assert store[1] == ("5", "+FLAGS", "(\\Seen)")
    assert res["result"] == "read"
    assert FakeIMAP.instances[0].selected == ('"INBOX"', False)


def test_mark_delete_without_yes_never_touches_the_server(capsys):
    with pytest.raises(SystemExit) as e:
        pmail.main(["mark", "5", "delete"])
    assert e.value.code == 2 and FakeIMAP.instances == []


def test_mark_delete_moves_to_trash(capsys):
    res = run_json(["mark", "5", "delete", "--yes"], capsys)
    move = [c for c in FakeIMAP.instances[0].commands if c[0] == "MOVE"][0]
    assert move[1] == ("5", '"Trash"')
    assert res["result"] == "moved_to_Trash"


def test_mark_delete_inside_trash_deletes_for_good(capsys):
    res = run_json(["mark", "5", "delete", "--yes", "--folder", "Trash"], capsys)
    cmds = [c[0] for c in FakeIMAP.instances[0].commands]
    assert "STORE" in cmds and "EXPUNGE" in cmds
    assert res["result"] == "expunged"


def test_folders_parses_the_LIST_response(capsys):
    res = run_json(["folders"], capsys)
    assert [f["name"] for f in res["folders"]] == ["Sent", "INBOX"]
    assert res["folders"][0]["attrs"] == ["\\Sent"]


# ---------------------------------------------------------------- helpers

def test_html_to_text_strips_tags_and_scripts():
    html = "<html><style>a{}</style><body><p>First</p><script>x()</script><p>Second</p></body>"
    assert pmail.html_to_text(html) == "First\nSecond"


def test_body_prefers_text_plain_over_html():
    raw = (b"Content-Type: multipart/alternative; boundary=B\r\n\r\n"
           b"--B\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nPlain text\r\n"
           b"--B\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<p>HTML</p>\r\n--B--\r\n")
    text, attachments = pmail.body_and_attachments(pmail.email.message_from_bytes(raw))
    assert text == "Plain text" and attachments == []


def test_imap_date_converts_the_format():
    assert pmail._imap_date("2026-08-05") == "05-Aug-2026"


def test_dec_handles_an_empty_header():
    assert pmail.dec(None) == "" and pmail.dec("") == ""


def test_a_missing_config_fails_with_a_readable_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("PMAIL_CONFIG", str(tmp_path / "missing.json"))
    with pytest.raises(SystemExit) as e:
        pmail.main(["credit"])
    assert e.value.code == 2
    assert "pmail setup --token" in capsys.readouterr().err
