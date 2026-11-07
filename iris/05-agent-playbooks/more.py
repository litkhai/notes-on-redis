"""Agent Playbooks, the remaining parts: a skill (package, upload, publish, discover, load), and the open
proposal from lab.py reviewed, edited, accepted and published. Same playbook and key as lab.py (.env).
usage: .venv/bin/python more.py skill|proposal
"""
import base64
import io
import os
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
for line in (HERE / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
from redis_agent_playbook import models  # noqa: E402
from redis_iris.agent_playbooks import AgentPlaybooks  # noqa: E402

pb = AgentPlaybooks.from_env()


def skill():
    root = HERE / "skills"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for f in sorted((root / "redis-free-plan-check").rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(root).as_posix())
    print(f"package: {len(buf.getvalue())} bytes, files {zipfile.ZipFile(io.BytesIO(buf.getvalue())).namelist()}")
    existing = [s for s in pb.client.list_skills().items if "redis-free-plan-check" in s.model_dump_json()]
    content = {"intents": ["Check whether a workload fits the free plan", "Which free plan limit does my app break"],
               "attributes": {"topic": "free-plan"}}
    pkg = base64.b64encode(buf.getvalue()).decode()
    if existing:
        draft = pb.client.append_skill_version(skill_id=existing[0].entry.entry_id if hasattr(existing[0], "entry") else existing[0].entry_id,
                                               package_base64=pkg, content=content)
    else:
        draft = pb.client.create_skill(package_base64=pkg, content=content)
    sid, ver = draft.entry.entry_id, draft.version.version
    print(f"uploaded: skill version {ver}, state {getattr(draft.version, 'state', None)}")
    pub = pb.client.publish_skill(skill_id=sid, version=ver)
    print("published:", getattr(getattr(pub, "publication", pub), "version", None) or "ok")
    for q in ("Will my app with 50 MB of sessions and 40 clients fit the free tier?",
              "무료 플랜에 TLS 필요한 서비스 올려도 돼?", "How much does Essentials cost in Seoul?"):
        d = pb.discover(q, limit=3)
        print(f"discover {q!r}\n   skills {[(s.title, round(s.score or 0, 2)) for s in d.skills]} faqs {[(f.entry_key, round(f.score or 0, 2)) for f in d.faqs]}")
    s = pb.skill(sid, version=ver)
    print("instructions (first line):", s.instructions.strip().splitlines()[0])
    res = next(r for r in s.resources if r.path == "references/limits.md")
    print("resource references/limits.md (first line):", pb.skill_resource(sid, res.resource_id, version=ver).text.splitlines()[0])


def proposal():
    inbox = pb.client.list_proposals(view=models.ProposalView.INBOX).items
    p = next(x for x in inbox if x.action.add.target.new_entry.entry_key == "active-active-seoul-tokyo")
    full = pb.client.get_proposal(proposal_id=p.proposal_id)
    faq = full.action.add.candidate.content.payload.faq
    print(f"proposal {full.state}, revision {full.revision}; draft answer: {faq.answer!r}")
    action = full.action.model_dump(exclude_unset=True, by_alias=False)
    action["add"]["candidate"]["content"]["payload"]["faq"]["answer"] = (
        "Active-Active needs Redis Cloud Pro or several Redis Software clusters; the free plan and Essentials do not "
        "offer it. On this site it is described as a design, not run (budget issue #12).")
    rev = pb.client.replace_proposal(proposal_id=full.proposal_id, action=action, expected_revision=full.revision)
    print(f"edited: revision {rev.revision}")
    acc = pb.client.accept_proposal(proposal_id=full.proposal_id, expected_revision=rev.revision)
    if not isinstance(acc.result, models.VersionCreated):
        raise SystemExit(f"unexpected acceptance result {acc.result!r}")
    receipt = acc.result.version_created
    print(f"accepted: FAQ version {receipt.version} created (not yet live)")
    print("discover before publish:", [(f.entry_key, round(f.score or 0, 2)) for f in pb.discover("Active-Active between Seoul and Tokyo", limit=2).faqs])
    pb.client.publish_faq(faq_id=receipt.entry_id, version=receipt.version)
    print("discover after publish: ", [(f.entry_key, round(f.score or 0, 2)) for f in pb.discover("Active-Active between Seoul and Tokyo", limit=2).faqs])
    print("proposal now:", pb.client.get_proposal(proposal_id=full.proposal_id).state)


if __name__ == "__main__":
    {"skill": skill, "proposal": proposal}[sys.argv[1]]()
