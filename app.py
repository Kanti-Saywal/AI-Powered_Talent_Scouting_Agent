import os, json, uuid, re, time, random, csv
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.secret_key = "talentscout-v4-2026"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ROLES_DATA = [
    {"role":"HR Manager","skills":["HRMS","Employee Relations","Recruitment","Compensation","Compliance","Workday","BambooHR"],"exp_range":(5,10),"locations":["Mumbai","Delhi","Bangalore","Hyderabad","Chennai"]},
    {"role":"Data Analyst","skills":["SQL","Python","Tableau","Power BI","Excel","Google Analytics","Looker"],"exp_range":(2,6),"locations":["Bangalore","Hyderabad","Pune","Chennai","Noida"]},
    {"role":"Zoho CRM Specialist","skills":["Zoho CRM","Zoho Flow","Deluge","API Integration","Sales Automation","Zoho Analytics","CRM Migration"],"exp_range":(2,6),"locations":["Chennai","Hyderabad","Pune","Bangalore","Coimbatore"]},
    {"role":"Product Manager","skills":["Product Strategy","Agile","SQL","Jira","User Research","Roadmapping","Figma"],"exp_range":(4,9),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Gurgaon"]},
    {"role":"Marketing Operations Manager","skills":["HubSpot","Marketo","Salesforce","Marketing Automation","SQL","Campaign Management","Pardot"],"exp_range":(4,9),"locations":["Bangalore","Mumbai","Gurgaon","Hyderabad","Delhi"]},
    {"role":"Finance Analyst","skills":["Financial Modeling","Excel","SQL","Power BI","FP&A","SAP","Tableau"],"exp_range":(2,7),"locations":["Mumbai","Delhi","Hyderabad","Pune","Bangalore"]},
    {"role":"Software Engineer","skills":["Python","Java","React","Node.js","PostgreSQL","Docker","AWS"],"exp_range":(2,8),"locations":["Bangalore","Hyderabad","Pune","Chennai","Noida"]},
    {"role":"Business Analyst","skills":["Requirements Gathering","SQL","Visio","Jira","Stakeholder Management","BPMN","Excel"],"exp_range":(3,8),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Pune"]},
    {"role":"Senior Data Engineer","skills":["Python","Apache Spark","Kafka","AWS","dbt","Airflow","Snowflake"],"exp_range":(5,9),"locations":["Bangalore","Hyderabad","Pune","Chennai","Noida"]},
    {"role":"Marketing Operations Analyst","skills":["HubSpot","Marketo","SQL","Excel","Campaign Analytics","Salesforce","Google Analytics"],"exp_range":(1,5),"locations":["Bangalore","Mumbai","Gurgaon","Hyderabad","Delhi"]},
    {"role":"CRM Administrator","skills":["Salesforce","HubSpot","Zoho CRM","Data Cleansing","CRM Configuration","API Integration","Workflows"],"exp_range":(2,6),"locations":["Bangalore","Hyderabad","Mumbai","Chennai","Pune"]},
    {"role":"Sales Operations Specialist","skills":["Salesforce","HubSpot","SQL","Excel","Pipeline Management","Revenue Analytics","Outreach"],"exp_range":(2,6),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Gurgaon"]},
    {"role":"Data Engineer","skills":["Python","SQL","AWS","ETL","Spark","Airflow","PostgreSQL"],"exp_range":(2,6),"locations":["Bangalore","Hyderabad","Pune","Chennai","Noida"]},
    {"role":"Talent Acquisition Specialist","skills":["Sourcing","LinkedIn Recruiter","ATS","Interviewing","Employer Branding","Naukri","Boolean Search"],"exp_range":(2,7),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Pune"]},
    {"role":"HRBP","skills":["HR Business Partnering","Employee Relations","Performance Management","Succession Planning","Change Management","HRMS","L&D"],"exp_range":(5,10),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Pune"]},
    {"role":"SDR","skills":["Cold Calling","Email Outreach","Salesforce","LinkedIn Sales Navigator","Prospecting","CRM","HubSpot"],"exp_range":(0,3),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Gurgaon"]},
    {"role":"RevOps Manager","skills":["Salesforce","HubSpot","Revenue Analytics","SQL","Process Automation","Clari","Tableau"],"exp_range":(5,9),"locations":["Bangalore","Mumbai","Gurgaon","Hyderabad","Delhi"]},
    {"role":"Customer Success Manager","skills":["Customer Onboarding","Salesforce","Gainsight","QBR","Churn Management","Excel","Stakeholder Management"],"exp_range":(3,8),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Pune"]},
    {"role":"Account Executive","skills":["B2B Sales","Salesforce","Negotiation","Pipeline Management","Cold Outreach","Demos","CRM"],"exp_range":(2,7),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Gurgaon"]},
    {"role":"RevOps Analyst","skills":["Salesforce","SQL","HubSpot","Excel","Revenue Analytics","Pipeline Analytics","Looker"],"exp_range":(1,5),"locations":["Bangalore","Mumbai","Gurgaon","Hyderabad","Delhi"]},
    {"role":"Customer Success Lead","skills":["Customer Onboarding","Gainsight","Salesforce","Team Leadership","Churn Reduction","NPS","QBR"],"exp_range":(5,9),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Pune"]},
    {"role":"Data Operations Manager","skills":["Data Governance","SQL","HubSpot","Salesforce","Python","ETL","CRM"],"exp_range":(5,9),"locations":["Bangalore","Hyderabad","Mumbai","Chennai","Pune"]},
    {"role":"HubSpot Specialist","skills":["HubSpot","Marketing Hub","Sales Hub","Workflows","HubSpot CMS","Email Automation","CRM"],"exp_range":(1,5),"locations":["Bangalore","Mumbai","Hyderabad","Delhi","Pune"]},
    {"role":"Recruiter","skills":["Sourcing","LinkedIn Recruiter","Boolean Search","ATS","Naukri","Stakeholder Management","Interviewing"],"exp_range":(1,5),"locations":["Bangalore","Mumbai","Delhi","Hyderabad","Pune"]},
]

FIRST = ["Priya","Arjun","Sneha","Rohan","Aisha","Vikram","Divya","Karan","Meera","Rahul",
         "Ananya","Siddharth","Pooja","Nikhil","Kavya","Ravi","Shreya","Amit","Neha","Rajesh",
         "Sunita","Deepak","Swati","Manish","Pallavi","Varun","Richa","Gaurav","Tanvi","Aditya"]
LAST  = ["Sharma","Mehta","Patel","Gupta","Khan","Nair","Reddy","Singh","Iyer","Verma",
         "Joshi","Malhotra","Banerjee","Rao","Pillai","Tiwari","Kapoor","Mishra","Pandey","Shah"]

random.seed(42)
POOL = []
n = 1
for rd in ROLES_DATA:
    for _ in range(10):
        sk = list(rd["skills"]); random.shuffle(sk); sk = sk[:random.randint(5,7)]
        POOL.append({"id":"C{:04d}".format(n),
            "name":"{} {}".format(random.choice(FIRST), random.choice(LAST)),
            "title":rd["role"], "location":"{}, India".format(random.choice(rd["locations"])),
            "skills":sk, "experience_years":random.randint(*rd["exp_range"]), "source":"builtin"})
        n += 1

sessions = {}
cv_jobs  = {}

SVOC = ["python","sql","java","javascript","react","node.js","aws","azure","gcp","docker",
    "kubernetes","spark","kafka","airflow","dbt","snowflake","tableau","power bi","salesforce",
    "hubspot","zoho crm","marketo","pardot","gainsight","excel","jira","figma","agile",
    "machine learning","tensorflow","pytorch","etl","data governance","postgresql","mongodb",
    "terraform","git","workday","bamboohr","sap","looker","google analytics","linkedin recruiter",
    "boolean search","ats","naukri","cold calling","email outreach","b2b sales","negotiation",
    "crm","qbr","nps","financial modeling","fp&a","requirements gathering","user research",
    "product strategy","employer branding","change management","succession planning","mlflow",
    "rest api","revenue analytics","pipeline management","outreach","clari","gainsight",
    "churn management","customer onboarding","b2b","linkedin sales navigator","prospecting",
    "campaign management","demand generation","lead generation","data quality","data cleansing",
    "sql server","mysql","redshift","bigquery","databricks","apache spark","pandas","numpy"]

TVOC = ["data operations manager","senior data engineer","data engineer","data scientist",
    "ml engineer","machine learning engineer","software engineer","data analyst","product manager",
    "hr manager","hrbp","recruiter","talent acquisition specialist","zoho crm specialist",
    "marketing operations manager","marketing operations analyst","finance analyst",
    "business analyst","sales operations specialist","crm administrator","hubspot specialist",
    "revops manager","revops analyst","customer success manager","customer success lead",
    "account executive","sdr","software developer","full stack developer","demand gen",
    "demand generation manager","revenue operations","gtm manager","sales development representative"]

def pdf_text(path):
    # Try pdfplumber first (text-based PDFs)
    try:
        import pdfplumber
        t = ""
        with pdfplumber.open(path) as pdf:
            for pg in pdf.pages:
                x = pg.extract_text()
                if x: t += x + "\n"
        if t.strip() and len(t.strip()) > 50:
            return t.strip()
    except: pass
    # Fallback: OCR for image/scanned PDFs
    try:
        import pytesseract
        from pdf2image import convert_from_path
        pages = convert_from_path(path, dpi=200)
        t = ""
        for page in pages:
            t += pytesseract.image_to_string(page) + "\n"
        return t.strip()
    except: return ""

def docx_text(path):
    try:
        from docx import Document
        return "\n".join(p.text for p in Document(path).paragraphs if p.text.strip())
    except: return ""

def parse_cv(text, fname, idx):
    lo = text.lower()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    # Name extraction
    name = os.path.splitext(fname)[0].replace("_"," ").replace("-"," ").title()
    for line in lines[:10]:
        w = line.split()
        if 2 <= len(w) <= 5 and all(x[0].isupper() for x in w if x.isalpha() and len(x)>1):
            if not any(k in line.lower() for k in ["email","phone","@","http","skill","exp",
               "summary","edu","linkedin","address","mobile","objective","profile","curriculum"]):
                name = line; break
    # Title extraction
    title = "Professional"
    for t in TVOC:
        if t in lo: title = t.title(); break
    # Experience extraction
    exp = 0
    for pat in [r"(\d+)\+?\s*years?\s*of\s*experience",
                r"(\d+)\+?\s*years?\s*experience",
                r"experience[:\s]+(\d+)\+?\s*years?"]:
        m = re.search(pat, lo)
        if m: exp = max(exp, int(m.group(1)))
    if exp == 0:
        yrs = sorted(set(int(y) for y in re.findall(r"\b(20\d{2})\b", text)))
        if len(yrs) >= 2: exp = min(yrs[-1] - yrs[0], 30)
    # Location
    loc = "India"
    for city in ["bangalore","bengaluru","hyderabad","mumbai","pune","delhi","noida",
                 "gurgaon","gurugram","chennai","kolkata","ahmedabad","jaipur"]:
        if city in lo:
            loc = city.replace("bengaluru","bangalore").replace("gurugram","gurgaon").title() + ", India"
            break
    # Skills — expanded matching
    skills = []
    for s in SVOC:
        if s in lo and s.title() not in skills:
            skills.append(s.title())
    skills = skills[:12]
    if not skills: skills = ["Communication","Problem Solving","MS Office"]
    # Summary
    summ = next((l[:200] for l in lines if len(l)>50 and "@" not in l and "http" not in l
                 and not l.startswith("+91") and not l[0].isdigit()), "")
    if not summ: summ = "{} yrs experience as {}. Skills: {}.".format(exp, title, ", ".join(skills[:4]))
    return {"id":"CV{:04d}".format(idx), "name":name, "title":title, "location":loc,
            "skills":skills, "experience_years":min(exp,40), "summary":summ,
            "source":"uploaded_cv", "filename":fname}

# ── SCORING ────────────────────────────────────────────────────────────────────
def score(c, jd):
    req  = [s.lower() for s in jd.get("required_skills",[])]
    pref = [s.lower() for s in jd.get("preferred_skills",[])]
    cs   = [s.lower() for s in c["skills"]]
    rh   = [s for s in req  if any(s in x or x in s for x in cs)]
    ph   = [s for s in pref if any(s in x or x in s for x in cs)]
    rs   = (len(rh)/max(len(req),1))*60
    ps   = (len(ph)/max(len(pref),1))*20
    exp  = c["experience_years"]
    mn, mx = jd.get("experience_min",0), jd.get("experience_max",99)
    es   = 20 if mn<=exp<=mx else (15 if exp>mx else max(0,20-(mn-exp)*5))
    return min(100,round(rs+ps+es)), {
        "required_matched":rh,
        "required_missing":[s for s in req if s not in rh],
        "preferred_matched":ph,
        "breakdown":{"required_skills":round(rs),"preferred_skills":round(ps),"experience":round(es)}}

def parse_jd(txt):
    lo = txt.lower()
    found = [s for s in SVOC if s in lo]
    req  = [r.title() for r in (found[:5] if len(found)>=5 else found+["Communication"])[:5]]
    pref = [p.title() for p in found[5:8]]
    m = re.findall(r"(\d+)\s*[-to]+\s*(\d+)\s*years?", lo)
    mn, mx = (int(m[0][0]), int(m[0][1])) if m else (3,7)
    t = "Software Professional"
    for tv in TVOC:
        if tv in lo: t = tv.title(); break
    return {"role_title":t,"required_skills":req,"preferred_skills":pref,"experience_min":mn,"experience_max":mx}

# ── CHAT ENGINE ────────────────────────────────────────────────────────────────
RPOOL = {
    1:["Thanks for reaching out! Sounds interesting. Could you share more about the team and company culture?",
       "Hi! The role looks relevant to my background. What does the day-to-day look like?",
       "Appreciate the message. I am selectively open right now. What is the tech stack like?",
       "Good timing actually. I have been thinking about my next move. Can you tell me more?",
       "Always open to the right opportunity. What makes this role stand out?"],
    2:["That sounds promising. What is the compensation range and growth path?",
       "Interesting! What is the remote policy and team size?",
       "I like what I am hearing. What does success look like in the first 6 months?",
       "Could you tell me more about the hiring manager and the team culture?",
       "I am open to the right move. Is the team distributed or co-located?"],
    3:["This checks most of my boxes. Yes, let us set up a call. I am free this week.",
       "I would be open to a 30 min exploratory call. The growth path sounds compelling.",
       "Sounds like a genuine fit. I am available next Tuesday or Wednesday afternoon.",
       "I appreciate the transparency. Let us connect — send me a calendar invite.",
       "If comp is competitive I would love to chat. Let us set something up next week."]}

FU = ["Great to hear! The team is collaborative and ships fast. What matters most to you in your next role — scope, tech, or growth?",
      "We offer strong comp and full remote flexibility. Would you be open to a quick 20 min intro call this week?"]

def outreach(c, jd):
    role = jd.get("role_title","this role")
    sk   = c["skills"][0] if c["skills"] else "your background"
    fn   = c["name"].split()[0]
    ops  = ["Hi {}! Your {} experience caught my eye while searching for a {}.".format(fn,sk,role),
            "Hey {}, I came across your profile and was impressed by your {} background.".format(fn,sk),
            "Hi {}! We are hiring a {} and your profile stood out — especially your {} skills.".format(fn,role,sk)]
    cls  = ["Would you be open to a quick chat?",
            "Is this something you would be interested in exploring?",
            "Are you open to hearing more details?"]
    return random.choice(ops) + " " + random.choice(cls)

def get_reply(conv, c, jd):
    cmsgs  = [m["content"].lower() for m in conv if m["role"]=="candidate"]
    rmsgs  = [m["content"].lower() for m in conv if m["role"]=="recruiter"]
    said   = " ".join(cmsgs)
    lastr  = rmsgs[-1] if rmsgs else ""
    turn   = len(cmsgs) + 1
    if turn == 1: cat = 1
    elif any(w in lastr for w in ["salary","comp","pay","ctc","remote","flexible","package","lpa"]): cat = 2
    elif any(w in lastr for w in ["call","schedule","calendar","meet","next step","slot","week","available"]): cat = 3
    elif turn >= 3: cat = 3 if random.random() > 0.35 else 2
    else: cat = 2
    unused = [r for r in RPOOL[cat] if r[:30].lower() not in said]
    return random.choice(unused if unused else RPOOL[cat])

def interest(conv):
    txt = " ".join(m["content"].lower() for m in conv if m["role"]=="candidate")
    pos = ["open to","happy to","sounds great","call","calendar","interested","love to","yes",
           "excited","definitely","next step","available","compelling","great fit","connect",
           "would be open","free this week","sounds good","let us"]
    neg = ["not interested","not looking","happy where","no thanks","not the right","not now","pass"]
    s   = 50 + sum(7 for w in pos if w in txt) - sum(14 for w in neg if w in txt)
    return min(95, max(20, s + random.randint(-3,3)))

def suggest(conv, jd):
    role = jd.get("role_title","this role")
    turn = len([m for m in conv if m["role"]=="candidate"])
    said = " ".join(m["content"].lower() for m in conv if m["role"]=="recruiter")
    pool = {
        0:["We are building a world-class {} team with real ownership. What kind of work excites you most right now?".format(role),
           "The team is fully remote and growing fast. What is most important to you in your next move?",
           "The {} role has great scope and cross-functional impact. Are you open to exploring it further?".format(role)],
        1:["The team is about 8 people, very collaborative. What does your ideal work setup look like?",
           "We are targeting candidates with your exact background. What would make you say yes to a new opportunity?",
           "We offer strong comp and remote flexibility. What is your current notice period?"],
        2:["Would you be open to a 20 min intro call? No pressure, just to see if there is a mutual fit.",
           "I can share the full JD and company deck right now if that helps. Shall I go ahead?",
           "If everything checks out, would next week work for a call with the hiring manager?"]}
    p = pool.get(min(turn,2), pool[2])
    f = [s for s in p if not any(w in said for w in s.lower().split()[:4])]
    return (f if f else p)[:3]

# ── CSV EXPORT of parsed CV skills ────────────────────────────────────────────
def save_parsed_to_csv(candidates):
    csv_path = os.path.join(os.path.dirname(__file__), "parsed_candidates.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","name","title","location","experience_years","skills","filename"])
        w.writeheader()
        for c in candidates:
            w.writerow({**{k:c.get(k,"") for k in ["id","name","title","location","experience_years","filename"]},
                        "skills":", ".join(c.get("skills",[]))})

# ── ROUTES ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index(): return render_template("index.html")

@app.route("/api/parse-jd", methods=["POST"])
def api_parse_jd():
    d  = request.get_json()
    jd = d.get("jd_text","").strip()
    if not jd: return jsonify({"error":"JD text required"}), 400
    sid = str(uuid.uuid4())
    p   = parse_jd(jd)
    sessions[sid] = {"jd_text":jd,"jd_parsed":p,"candidates":[]}
    return jsonify({"session_id":sid,"jd_parsed":p})

@app.route("/api/upload-cvs", methods=["POST"])
def api_upload_cvs():
    files = request.files.getlist("files")
    if not files: return jsonify({"error":"No files"}), 400
    saved = []
    for f in files:
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in {".pdf",".docx",".doc"}: continue
        safe = uuid.uuid4().hex + ext
        path = os.path.join(UPLOAD_FOLDER, safe)
        f.save(path)
        saved.append({"path":path,"filename":f.filename})
    if not saved: return jsonify({"error":"No valid PDF/DOCX files"}), 400
    jid = str(uuid.uuid4())
    cv_jobs[jid] = {"total":len(saved),"done":0,"candidates":[],"errors":[],"files":saved,"status":"pending"}
    return jsonify({"job_id":jid,"total":len(saved)})

@app.route("/api/parse-cvs-stream/<jid>")
def api_parse_stream(jid):
    if jid not in cv_jobs: return jsonify({"error":"Invalid job"}), 404
    def gen():
        job = cv_jobs[jid]; job["status"] = "running"
        for i, fi in enumerate(job["files"]):
            path, fname = fi["path"], fi["filename"]
            ext  = os.path.splitext(fname)[1].lower()
            cand = None
            try:
                txt = pdf_text(path) if ext == ".pdf" else docx_text(path)
                if not txt.strip(): raise ValueError("No text extracted")
                cand = parse_cv(txt, fname, i+1)
                job["candidates"].append(cand)
            except Exception as e:
                job["errors"].append({"file":fname,"error":str(e)})
            finally:
                try: os.remove(path)
                except: pass
            job["done"] = i + 1
            pay = {"done":job["done"],"total":job["total"],"filename":fname,
                   "success":cand is not None,
                   "candidate":{k:v for k,v in cand.items() if k!="source"} if cand else None}
            yield "data: {}\n\n".format(json.dumps(pay))
            time.sleep(0.3)
        # Save to CSV for reference
        if job["candidates"]:
            save_parsed_to_csv(job["candidates"])
        job["status"] = "complete"
        yield "data: {}\n\n".format(json.dumps({
            "done":job["total"],"total":job["total"],"complete":True,
            "count":len(job["candidates"])}))
    return Response(stream_with_context(gen()), mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.route("/api/cv-parse-result/<jid>")
def api_cv_result(jid):
    if jid not in cv_jobs: return jsonify({"error":"Invalid job"}), 404
    j = cv_jobs[jid]
    return jsonify({"candidates":j["candidates"],"status":j["status"]})

@app.route("/api/discover-candidates", methods=["POST"])
def api_discover():
    d    = request.get_json()
    sid  = d.get("session_id")
    mode = d.get("mode","builtin")
    jid  = d.get("job_id","")
    if not sid or sid not in sessions: return jsonify({"error":"Invalid session"}), 400
    sess = sessions[sid]
    jdp  = sess["jd_parsed"]
    if mode == "uploaded":
        pool = cv_jobs.get(jid,{}).get("candidates",[])
        if not pool: return jsonify({"error":"No parsed CVs found. Please parse CVs first."}), 400
    else:
        pool = POOL
    # Score ALL candidates in pool, return top 6
    scored = []
    for c in pool:
        sc, ex = score(c, jdp)
        scored.append({**c, "match_score":sc, "explanation":ex,
                       "interest_score":None, "conversation":[]})
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    top = scored[:6]
    # Generate personalised outreach for each
    for c in top:
        msg = outreach(c, jdp)
        c["conversation"]    = [{"role":"recruiter","content":msg}]
        c["outreach_message"] = msg
    sess["candidates"] = top
    return jsonify({"candidates":[{
        "id":c["id"],"name":c["name"],"title":c["title"],"location":c["location"],
        "skills":c["skills"],"experience_years":c["experience_years"],
        "match_score":c["match_score"],"explanation":c["explanation"],
        "outreach_message":c["outreach_message"],
        "source":c.get("source","builtin"),"filename":c.get("filename","")} for c in top]})

@app.route("/api/chat-turn", methods=["POST"])
def api_chat():
    d   = request.get_json()
    sid = d.get("session_id"); cid = d.get("candidate_id")
    msg = d.get("recruiter_message","").strip()
    if not sid or sid not in sessions: return jsonify({"error":"Invalid session"}), 400
    sess = sessions[sid]
    cand = next((c for c in sess["candidates"] if c["id"]==cid), None)
    if not cand: return jsonify({"error":"Candidate not found"}), 404
    conv = cand["conversation"]
    if msg: conv.append({"role":"recruiter","content":msg})
    reply = get_reply(conv, cand, sess["jd_parsed"])
    conv.append({"role":"candidate","content":reply})
    sc = interest(conv); cand["interest_score"] = sc
    return jsonify({"candidate_reply":reply,"interest_score":sc,"conversation":conv})

@app.route("/api/suggest-reply", methods=["POST"])
def api_suggest():
    d    = request.get_json()
    sid  = d.get("session_id"); cid = d.get("candidate_id")
    sess = sessions.get(sid,{})
    cand = next((c for c in sess.get("candidates",[]) if c["id"]==cid), None)
    conv = cand["conversation"] if cand else []
    jdp  = sess.get("jd_parsed",{})
    return jsonify({"suggestions": suggest(conv, jdp)})

@app.route("/api/engage-all", methods=["POST"])
def api_engage():
    d   = request.get_json(); sid = d.get("session_id")
    if not sid or sid not in sessions: return jsonify({"error":"Invalid session"}), 400
    sess = sessions[sid]
    if not sess.get("candidates"):
        return jsonify({"error":"No candidates found. Please discover candidates first."}), 400
    def engage_one(cand):
        conv = list(cand["conversation"])
        for t in range(1,4):
            conv.append({"role":"candidate","content":get_reply(conv,cand,sess["jd_parsed"])})
            if t < 3: conv.append({"role":"recruiter","content":FU[t-1]})
        return cand["id"], conv, interest(conv)
    with ThreadPoolExecutor(max_workers=6) as ex:
        for cid, conv, sc in ex.map(engage_one, sess["candidates"]):
            c = next(x for x in sess["candidates"] if x["id"]==cid)
            c["conversation"] = conv; c["interest_score"] = sc
    sl = []
    for c in sess["candidates"]:
        combined = round(c["match_score"]*0.6 + (c["interest_score"] or 50)*0.4)
        sl.append({"id":c["id"],"name":c["name"],"title":c["title"],"location":c["location"],
            "skills":c["skills"],"experience_years":c["experience_years"],
            "match_score":c["match_score"],"interest_score":c["interest_score"],
            "combined_score":combined,"explanation":c["explanation"],
            "conversation":c["conversation"],"source":c.get("source","builtin"),
            "filename":c.get("filename","")})
    sl.sort(key=lambda x: x["combined_score"], reverse=True)
    sess["shortlist"] = sl
    return jsonify({"shortlist":sl})

if __name__ == "__main__":
    print("\n  TalentScout AI v4 -> http://localhost:5001\n")
    app.run(debug=True, port=5001)
