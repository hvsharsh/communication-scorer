from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


rubric = pd.read_excel("rubric.xlsx")
model = SentenceTransformer("all-MiniLM-L6-v2")
rubric["embedding"] = rubric["description"].apply(lambda x: model.encode(str(x), convert_to_tensor=True))

class Transcript(BaseModel):
    transcript: str

def score_criterion(transcript, row):
    transcript_text = transcript.lower()
    t_emb = model.encode(transcript, convert_to_tensor=True)
    sim = util.cos_sim(t_emb, row["embedding"]).item()
    similarity_score = max(0, (sim+1)/2)
    keywords = str(row["keywords"]).split(",")
    found=[k.strip().lower() for k in keywords if k.strip().lower() in transcript_text]
    keyword_score=len(found)/max(1,len(keywords))
    raw=0.5*keyword_score+0.5*similarity_score
    return raw, found, similarity_score

@app.post("/score")
def get_score(data: Transcript):
    text=data.transcript
    word_count=len(text.split())
    results=[]
    total_weight=rubric["weight"].sum()
    final_score=0
    for _,row in rubric.iterrows():
        raw,found,sim=score_criterion(text,row)
        weighted=raw*(row["weight"]/total_weight)
        final_score+=weighted
        results.append({
            "criterion":row["criterion"],
            "keywords_found":found,
            "similarity":round(sim,3),
            "score":round(raw*100,2),
            "feedback":f"Found keywords: {found}, Similarity: {round(sim,2)}"
        })
    return {"overall_score":round(final_score*100,2),"word_count":word_count,"criteria":results}
